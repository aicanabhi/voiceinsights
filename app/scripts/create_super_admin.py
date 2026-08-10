import asyncio
import sys

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.enums import UserRole
from app.models.user import User


async def create_super_admin():

    email = settings.SUPER_ADMIN_EMAIL
    password = settings.SUPER_ADMIN_PASSWORD

    if not email or not password:
        print(
            "[ERROR] SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD must be set "
            "in your .env before seeding."
        )
        return 1

    async with AsyncSessionLocal() as db:

        # The role cannot be granted through the API, so an existing Super
        # Admin under a different email still means the system is seeded.
        result = await db.execute(
            select(User).where(
                User.role == UserRole.SUPER_ADMIN
            )
        )

        existing_super_admin = result.scalars().first()

        if existing_super_admin:
            print(
                f"[OK] Super Admin already exists: {existing_super_admin.email}"
            )
            return 0

        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )

        conflicting_user = result.scalar_one_or_none()

        if conflicting_user:
            print(
                f"[ERROR] {email} is already taken by a "
                f"{conflicting_user.role.value}. Use a different "
                "SUPER_ADMIN_EMAIL."
            )
            return 1

        super_admin = User(
            full_name=settings.SUPER_ADMIN_NAME,
            email=email,
            phone=settings.SUPER_ADMIN_PHONE,
            password_hash=hash_password(password),
            role=UserRole.SUPER_ADMIN,
            organization_id=None,
            team_id=None,
            is_active=True
        )

        db.add(super_admin)

        await db.commit()

        print(f"[OK] Super Admin created successfully: {email}")

        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(create_super_admin()))
