from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.provider_models import PROVIDER_MODELS
from app.models.enums import TranscriptProvider, UserRole
from app.models.user import User
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization_agent import (
    OrganizationAgentCreate,
    OrganizationAgentResponse,
    OrganizationAgentUpdate,
)


class OrganizationAgentService:

    @staticmethod
    def _ensure_can_read(
        current_user: User,
        organization_id: int
    ):
        """SUPER_ADMIN manages every organization's agents. ORG_ADMIN may read
        its own organization only -- and a NULL scope must never match."""

        if current_user.role == UserRole.SUPER_ADMIN:
            return

        if current_user.role == UserRole.ORG_ADMIN:

            if (
                current_user.organization_id is None
                or current_user.organization_id != organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can access only your organization's agents."
                )

            return

        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access organization agents."
        )

    @staticmethod
    def _validate_model(
        provider: TranscriptProvider,
        model: str
    ):

        allowed = PROVIDER_MODELS.get(provider.value, [])

        if model not in allowed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"'{model}' is not a valid {provider.value} model. "
                    f"Allowed: {', '.join(allowed)}"
                )
            )

    @staticmethod
    async def _ensure_organization_exists(
        db: AsyncSession,
        organization_id: int
    ):

        organization = await OrganizationRepository.get_by_id(
            db,
            organization_id
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

    @staticmethod
    async def create_agent(
        db: AsyncSession,
        data: OrganizationAgentCreate
    ) -> OrganizationAgentResponse:

        await OrganizationAgentService._ensure_organization_exists(
            db,
            data.organization_id
        )

        OrganizationAgentService._validate_model(
            data.provider,
            data.model
        )

        agent = {
            "organization_id": data.organization_id,
            "agent_name": data.agent_name,
            "provider": data.provider.value,
            "model": data.model,
            "language": data.language.value,
            "system_prompt": data.system_prompt,
            "security_key": data.security_key,
            "status": data.status.value,
        }

        try:
            agent["_id"] = await OrganizationAgentRepository.create(agent)

        except DuplicateKeyError:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"A {data.provider.value} agent already exists for this "
                    "organization. Update it instead."
                )
            )

        return OrganizationAgentResponse.from_document(agent)

    @staticmethod
    async def get_agents_for_organization(
        organization_id: int,
        current_user: User
    ) -> list[OrganizationAgentResponse]:

        OrganizationAgentService._ensure_can_read(
            current_user,
            organization_id
        )

        documents = await OrganizationAgentRepository.get_by_organization(
            organization_id
        )

        return [
            OrganizationAgentResponse.from_document(document)
            for document in documents
        ]

    @staticmethod
    async def get_agent(
        organization_id: int,
        provider: TranscriptProvider,
        current_user: User
    ) -> OrganizationAgentResponse:

        OrganizationAgentService._ensure_can_read(
            current_user,
            organization_id
        )

        document = await OrganizationAgentRepository.get_by_organization_provider(
            organization_id,
            provider.value
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No {provider.value} agent configured for this "
                    "organization."
                )
            )

        return OrganizationAgentResponse.from_document(document)

    @staticmethod
    async def get_all_agents() -> list[OrganizationAgentResponse]:

        documents = await OrganizationAgentRepository.get_all()

        return [
            OrganizationAgentResponse.from_document(document)
            for document in documents
        ]

    @staticmethod
    async def update_agent(
        organization_id: int,
        provider: TranscriptProvider,
        data: OrganizationAgentUpdate
    ) -> OrganizationAgentResponse:

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields to update."
            )

        if "model" in update_data:
            OrganizationAgentService._validate_model(
                provider,
                update_data["model"]
            )

        for enum_field in ("language", "status"):
            if update_data.get(enum_field) is not None:
                update_data[enum_field] = update_data[enum_field].value

        document = await OrganizationAgentRepository.update(
            organization_id,
            provider.value,
            update_data
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No {provider.value} agent configured for this "
                    "organization."
                )
            )

        return OrganizationAgentResponse.from_document(document)

    @staticmethod
    async def delete_agent(
        organization_id: int,
        provider: TranscriptProvider
    ):

        deleted = await OrganizationAgentRepository.delete(
            organization_id,
            provider.value
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No {provider.value} agent configured for this "
                    "organization."
                )
            )

        return {
            "message": f"{provider.value} agent deleted successfully."
        }
