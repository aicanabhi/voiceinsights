from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Float
)

from sqlalchemy.orm import relationship

from app.db.base import Base


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transcript_id = Column(
        Integer,
        ForeignKey(
            "transcripts.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    speaker = Column(Integer)

    text = Column(
        Text,
        nullable=False
    )

    start_time = Column(Float)

    end_time = Column(Float)

    confidence = Column(Float)

    transcript = relationship(
        "Transcript",
        back_populates="segments"
    )