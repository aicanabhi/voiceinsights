from app.models.transcript_segment import TranscriptSegment


class TranscriptSegmentService:


    @staticmethod
    async def create_segments(
        db,
        transcript_id,
        segments
    ):

        objects=[]

        for seg in segments:

            obj=TranscriptSegment(
                transcript_id=transcript_id,
                speaker=seg["speaker"],
                start_time=seg["start"],
                end_time=seg["end"],
                text=seg["text"],
                confidence=seg.get("confidence")
            )

            objects.append(obj)


        db.add_all(objects)

        await db.commit()

        return objects