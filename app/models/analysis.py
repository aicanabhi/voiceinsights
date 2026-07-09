from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Float,
    DateTime
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Analysis(Base):
    __tablename__ = "analysis"

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

    summary = Column(Text)

    sentiment = Column(Text)

    compliance_score = Column(Float)

    violations = Column(Text)

    ai_feedback = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    transcript = relationship(
        "Transcript"
    )