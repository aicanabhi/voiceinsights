import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import hash_password


async def create_super_admin():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(User).where(
                User.email == "superadmin@gmail.com"
            )
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("✅ Super Admin already exists.")
            return

        super_admin = User(
            full_name="Super Admin",
            email="superadmin@gmail.com",
            phone="9999999999",
            password_hash=hash_password("Admin@123"),
            role=UserRole.SUPER_ADMIN,
            organization_id=None,
            team_id=None,
            is_active=True
        )

        db.add(super_admin)

        await db.commit()

        print("✅ Super Admin created successfully.")


if __name__ == "__main__":
    asyncio.run(create_super_admin())