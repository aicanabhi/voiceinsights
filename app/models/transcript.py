from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    String,
    DateTime
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    media_id = Column(
        Integer,
        ForeignKey(
            "media.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    transcript = Column(
        Text,
        nullable=False
    )

    language = Column(
        String(20),
        default="en"
    )

    status = Column(
        String(20),
        default="PENDING"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    media = relationship(
        "Media",
        back_populates="transcripts"
    )

    segments = relationship(
        "TranscriptSegment",
        back_populates="transcript",
        cascade="all, delete-orphan"
    )