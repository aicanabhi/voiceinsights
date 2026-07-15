from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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