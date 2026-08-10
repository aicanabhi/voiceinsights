from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    Index,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import MediaStatus


class Media(Base):
    __tablename__ = "media"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    calling_agent_id = Column(
        Integer,
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=True
    )

    uploaded_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    original_filename = Column(
        String(255),
        nullable=False
    )

    stored_filename = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_size = Column(Integer)

    content_type = Column(
        String(100)
    )

    status = Column(
        Enum(MediaStatus),
        nullable=False,
        default=MediaStatus.PENDING,
        index=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    provider = Column(
        String(50),
        nullable=False
    )

    model = Column(
        String(100),
        nullable=False
    )

    language = Column(
        String(50),
        nullable=False
    )

    is_deleted = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # The worker polls on (status, created_at) -- oldest PENDING first.
    __table_args__ = (
        Index(
            "ix_media_status_created_at",
            "status",
            "created_at"
        ),
    )

    # Relationships

    organization = relationship(
        "Organization"
    )

    calling_agent = relationship(
        "User",
        foreign_keys=[calling_agent_id],
        back_populates="assigned_media"
    )


    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
        back_populates="uploaded_media"
    )

    transcripts = relationship(
        "Transcript",
        back_populates="media",
        cascade="all, delete-orphan"
    )

    analysis = relationship(
        "Analysis",
        back_populates="media",
        uselist=False,
        cascade="all, delete-orphan"
    )