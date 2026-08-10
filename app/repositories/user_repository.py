from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserUpdate


class UserRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User
    ):
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(User)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: int
    ):
        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_organization(
        db: AsyncSession,
        user_id: int
    ):
        # eager-loaded: the async session cannot lazy-load user.organization
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.organization)
            )
            .where(
                User.id == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def count_active_by_role(
        db: AsyncSession,
        role: UserRole
    ) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.role == role,
                User.is_active.is_(True)
            )
        )
        return result.scalar_one()

    @staticmethod
    async def get_by_email(
        db: AsyncSession,
        email: str
    ):
        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        user: User,
        data: UserUpdate
    ):
        update_data = data.model_dump(exclude_unset=True)

        password = update_data.pop("password", None)

        if password is not None:
            user.password_hash = hash_password(password)

        for key, value in update_data.items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete(
        db: AsyncSession,
        user: User
    ):
        await db.delete(user)
        await db.commit()

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User
    ):
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user