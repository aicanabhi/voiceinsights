from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    Float,
    Boolean,
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

    media_id = Column(
        Integer,
        ForeignKey(
            "media.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # AI Summary
    summary = Column(Text)

    # Positive / Negative / Neutral
    sentiment = Column(Text)

    # Compliance Score
    compliance_score = Column(Float)

    # Professionalism Score
    professionalism_score = Column(Float)

    # Empathy Score
    empathy_score = Column(Float)

    # Overall Score
    overall_score = Column(Float)

    # Greeting Rule
    greeting_followed = Column(
        Boolean,
        default=False
    )

    # Closing Rule
    closing_followed = Column(
        Boolean,
        default=False
    )

    # Rule Violations
    violations = Column(Text)

    # AI Suggestions
    recommendations = Column(Text)

    # Final AI Feedback
    ai_feedback = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    media = relationship(
        "Media",
        back_populates="analysis"
    )