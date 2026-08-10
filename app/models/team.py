from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        String(255),
        nullable=True
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

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_teams_organization_name",
        ),
    )

    organization = relationship(
        "Organization",
        back_populates="teams"
    )

    # Deleting a team must NOT delete its members -- users.team_id is
    # ON DELETE SET NULL, so leave the cascade to the database. A
    # delete-orphan cascade here would wipe the employees instead.
    users = relationship(
        "User",
        back_populates="team",
        passive_deletes=True
    )