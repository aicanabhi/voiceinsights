from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    email = Column(String(200), unique=True, nullable=False)

    phone = Column(String(20), nullable=True)

    address = Column(String(255), nullable=True)

    industry = Column(String(100), nullable=True)

    website = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    teams = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )