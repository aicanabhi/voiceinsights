from app.models.transcript_segment import TranscriptSegment


class TranscriptSegmentService:

    @staticmethod
    async def create_segments(
        db,
        transcript_id,
        segments
    ):
        """Persist canonical segments (see transcript_normalizer).

        Values are coerced defensively: `speaker` is an INTEGER column, and a
        provider handing back something like "speaker_0" would otherwise fail
        the insert and take the whole transcription down with it.
        """

        objects = []

        for seg in segments or []:

            text = (seg.get("text") or "").strip()

            if not text:
                continue

            try:
                speaker = int(seg.get("speaker") or 0)
            except (TypeError, ValueError):
                speaker = 0

            objects.append(
                TranscriptSegment(
                    transcript_id=transcript_id,
                    speaker=speaker,
                    start_time=seg.get("start"),
                    end_time=seg.get("end"),
                    text=text,
                    confidence=seg.get("confidence"),
                )
            )

        if not objects:
            return []

        db.add_all(objects)

        await db.commit()

        return objects
