from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


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

    agent_id = Column(
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

    upload_status = Column(
        String(30),
        default="UPLOADED"
    )

    is_deleted = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships

    organization = relationship(
        "Organization"
    )

    agent = relationship(
        "User",
        foreign_keys=[agent_id],
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