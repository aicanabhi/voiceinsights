from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(200),
        unique=True,
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )

    team = relationship(
        "Team",
        back_populates="users"
    )

    uploaded_media = relationship(
        "Media",
        foreign_keys="Media.uploaded_by",
        back_populates="uploader"
    )

    assigned_media = relationship(
        "Media",
        foreign_keys="Media.agent_id",
        back_populates="agent"
    )