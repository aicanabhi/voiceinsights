import asyncio
import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.provider_models import PROVIDER_MODELS
from app.constants.upload import (
    ALLOWED_CONTENT_TYPES,
    MAX_UPLOAD_BYTES,
    UPLOAD_CHUNK_BYTES,
)
from app.models.analysis import Analysis
from app.models.enums import (
    AgentStatus,
    MediaStatus,
    Sentiment,
    TranscriptProvider,
    UserRole,
)
from app.models.media import Media
from app.models.user import User

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)
from app.repositories.transcript_repository import TranscriptRepository
from app.repositories.transcript_segment_repository import (
    TranscriptSegmentRepository
)
from app.repositories.user_repository import UserRepository

from app.services.call_metrics import compute_call_metrics
from app.services.cartesia_service import CartesiaService
from app.services.deepgram_service import DeepgramService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.groq_service import GroqService
from app.services.transcript_service import TranscriptService
from app.services.transcript_segment_service import TranscriptSegmentService


UPLOAD_DIR = "uploads"
groq_service = GroqService()


class AgentConfigError(Exception):
    """The organization's agent config cannot drive a transcription."""


class MediaService:

    # ------------------------------------------------------------------
    # Enqueue side -- runs inside the HTTP request, must stay fast
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_can_attribute_to(current_user: User, calling_agent: User):
        """Who a call may be scored against.

        The uploader is not necessarily the agent on the call -- a team lead
        uploads for their members. But attribution drives every scorecard and
        dashboard, so it must be no wider than what the uploader manages.
        """

        if current_user.role in (UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN):
            return

        if current_user.role == UserRole.TEAM_LEAD:

            if (
                current_user.team_id is None
                or calling_agent.team_id != current_user.team_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can upload calls only for your own team."
                )

            return

        if calling_agent.id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can upload calls only for yourself."
            )

    @staticmethod
    async def _resolve_agent(
        organization_id: int,
        provider: TranscriptProvider
    ) -> dict:
        """Fetch and sanity-check the org's config for this provider.

        Raises AgentConfigError so the caller decides whether that is a 4xx
        (upload time) or a job failure (worker time).
        """

        agent = await OrganizationAgentRepository.get_by_organization_provider(
            organization_id=organization_id,
            provider=provider.value
        )

        if agent is None:
            raise AgentConfigError(
                f"No {provider.value} agent configured for this organization."
            )

        if agent.get("status") != AgentStatus.ACTIVE.value:
            raise AgentConfigError(
                f"The {provider.value} agent for this organization is inactive."
            )

        if not agent.get("security_key"):
            raise AgentConfigError(
                f"The {provider.value} agent has no API key configured."
            )

        if agent.get("model") not in PROVIDER_MODELS.get(provider.value, []):
            raise AgentConfigError(
                f"{agent.get('model')} is not a valid model "
                f"for {provider.value}."
            )

        return agent

    @staticmethod
    async def _store_upload(file: UploadFile) -> tuple[str, str, int]:
        """Stream one upload to disk, enforcing the size cap as it goes."""

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=415,
                detail=(
                    f"'{file.content_type}' is not a supported audio type. "
                    f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
                )
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        extension = os.path.splitext(file.filename or "")[1]
        stored_filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)

        file_size = 0

        try:
            with open(file_path, "wb") as buffer:

                while True:

                    chunk = await file.read(UPLOAD_CHUNK_BYTES)

                    if not chunk:
                        break

                    file_size += len(chunk)

                    if file_size > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            status_code=413,
                            detail=(
                                "Audio file is larger than "
                                f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
                            )
                        )

                    buffer.write(chunk)

        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        if file_size == 0:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="File is empty."
            )

        return stored_filename, file_path, file_size

    @staticmethod
    async def enqueue_uploads(
        db: AsyncSession,
        current_user: User,
        calling_agent_id: int,
        provider: TranscriptProvider,
        files: list[UploadFile]
    ) -> dict:
        """Accept 1..N recordings and queue them. Returns immediately -- the
        worker does the transcription."""

        organization_id = current_user.organization_id

        if organization_id is None:
            raise HTTPException(
                status_code=400,
                detail="Your account is not linked to an organization."
            )

        calling_agent = await UserRepository.get_by_id(db, calling_agent_id)

        if (
            calling_agent is None
            or calling_agent.organization_id != organization_id
        ):
            raise HTTPException(
                status_code=404,
                detail="Calling agent not found in your organization."
            )

        MediaService._ensure_can_attribute_to(current_user, calling_agent)

        # Checked once up front so a misconfigured org fails the whole request
        # instead of queueing jobs that are all guaranteed to fail.
        try:
            agent = await MediaService._resolve_agent(
                organization_id,
                provider
            )
        except AgentConfigError as e:
            raise HTTPException(status_code=400, detail=str(e))

        accepted, rejected = [], []

        for file in files:

            try:
                stored_filename, file_path, file_size = (
                    await MediaService._store_upload(file)
                )

            except HTTPException as e:
                # One bad file must not sink the rest of the batch.
                rejected.append({
                    "filename": file.filename,
                    "reason": e.detail,
                })
                continue

            media = Media(
                organization_id=organization_id,
                uploaded_by=current_user.id,
                calling_agent_id=calling_agent_id,
                original_filename=file.filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file_size,
                content_type=file.content_type,
                status=MediaStatus.PENDING,
                provider=provider.value,
                model=agent["model"],
                language=agent["language"],
            )

            media = await MediaRepository.create(db, media)

            accepted.append({
                "media_id": media.id,
                "filename": media.original_filename,
                "status": media.status,
            })

        return {
            "accepted": accepted,
            "rejected": rejected,
        }

    # ------------------------------------------------------------------
    # Worker side -- runs outside the request, may take minutes
    # ------------------------------------------------------------------

    @staticmethod
    async def _transcribe(media: Media, agent: dict) -> dict:
        """Blocking provider SDK / HTTP call, kept off the event loop."""

        provider = TranscriptProvider(media.provider)
        api_key = agent["security_key"]

        if provider == TranscriptProvider.DEEPGRAM:
            return await asyncio.to_thread(
                DeepgramService(api_key).transcribe,
                media.file_path,
                media.model,
                media.language,
            )

        if provider == TranscriptProvider.ELEVENLABS:
            return await asyncio.to_thread(
                ElevenLabsService(api_key).transcribe,
                media.file_path,
                media.model,
            )

        if provider == TranscriptProvider.CARTESIA:
            return await asyncio.to_thread(
                CartesiaService(api_key).transcribe,
                media.file_path,
                media.model,
            )

        raise AgentConfigError(f"Unsupported provider '{media.provider}'.")

    @staticmethod
    async def process_media(
        db: AsyncSession,
        media: Media
    ) -> Media:
        """Transcribe + analyse one claimed job.

        The agent config is re-read here rather than carried from upload time,
        so a rotated API key or an edited prompt takes effect on retry.
        """

        if not os.path.exists(media.file_path):
            raise AgentConfigError(
                "Audio file is missing from storage."
            )

        agent = await MediaService._resolve_agent(
            media.organization_id,
            TranscriptProvider(media.provider)
        )

        transcript_result = await MediaService._transcribe(media, agent)

        transcript_obj = await TranscriptService.create_transcript(
            db=db,
            media_id=media.id,
            transcript_text=transcript_result["transcript"],
            language=transcript_result["language"],
            status="COMPLETED",
        )

        await TranscriptSegmentService.create_segments(
            db,
            transcript_obj.id,
            transcript_result["speaker_segments"],
        )

        await MediaRepository.mark_status(
            db,
            media,
            MediaStatus.TRANSCRIBED,
        )

        ai_result = await asyncio.to_thread(
            groq_service.analyze_transcript,
            transcript_result["transcript"],
            agent["system_prompt"],
        )

        analysis = Analysis(
            media_id=media.id,
            summary=ai_result["summary"],
            # normalised on write so dashboard counts cannot miss a row
            # because the model answered "positive" instead of "Positive"
            sentiment=Sentiment.normalize(ai_result.get("sentiment")),
            compliance_score=ai_result["compliance_score"],
            professionalism_score=ai_result["professionalism_score"],
            empathy_score=ai_result["empathy_score"],
            overall_score=ai_result["overall_score"],
            greeting_followed=ai_result["greeting_followed"],
            closing_followed=ai_result["closing_followed"],
            violations=ai_result["violations"],
            recommendations=ai_result["recommendations"],
            ai_feedback=ai_result["ai_feedback"],
        )

        await AnalysisRepository.create(db, analysis)

        return await MediaRepository.mark_status(
            db,
            media,
            MediaStatus.COMPLETED,
        )

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    @staticmethod
    async def get_all_files(
        db: AsyncSession,
        current_user: User
    ):
        return await MediaRepository.get_all_for_user(db, current_user)

    @staticmethod
    async def get_media(
        db: AsyncSession,
        media_id: int,
        current_user: User
    ):
        media = await MediaRepository.get_by_id_for_user(
            db,
            media_id,
            current_user
        )

        if media is None:
            raise HTTPException(
                status_code=404,
                detail="Media not found."
            )

        return media

    @staticmethod
    async def get_call_result(
        db: AsyncSession,
        media_id: int,
        current_user: User
    ) -> dict:
        """Media + transcript + segments + analysis for one call.

        Callers only ever hold a media_id, so this is the single read that
        backs both the detail view and status polling. The pieces are null
        until the worker produces them.
        """

        media = await MediaService.get_media(db, media_id, current_user)

        transcript = await TranscriptRepository.get_by_media_id(db, media.id)

        segments = []

        if transcript is not None:
            segments = await TranscriptSegmentRepository.get_by_transcript(
                db,
                transcript.id
            )

        analysis = await AnalysisRepository.get_by_media(db, media.id)

        return {
            "media": media,
            "transcript": transcript,
            "segments": segments,
            "analysis": analysis,
            "metrics": compute_call_metrics(segments),
            "audio_url": f"/api/v1/media/{media.id}/audio",
            "has_diarization": bool(segments),
        }

    @staticmethod
    async def get_audio_file(
        db: AsyncSession,
        media_id: int,
        current_user: User
    ):
        """Resolve the on-disk audio for a media row the caller may see."""

        media = await MediaService.get_media(db, media_id, current_user)

        if not os.path.exists(media.file_path):
            raise HTTPException(
                status_code=404,
                detail="Audio file is missing from storage."
            )

        return media
