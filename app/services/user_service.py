from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository

from app.core.security import hash_password


class UserService:

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate
    ):

        # Check email already exists
        existing_user = await UserRepository.get_by_email(
            db,
            user_data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

        # Check organization exists
        if user_data.organization_id is not None:

            organization = await OrganizationRepository.get_by_id(
                db,
                user_data.organization_id
            )

            if not organization:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found."
                )

        # Check team exists
        if user_data.team_id is not None:

            team = await TeamRepository.get_by_id(
                db,
                user_data.team_id
            )

            if not team:
                raise HTTPException(
                    status_code=404,
                    detail="Team not found."
                )

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            organization_id=user_data.organization_id,
            team_id=user_data.team_id,
        )

        return await UserRepository.create(
            db,
            user
        )

    @staticmethod
    async def get_all_users(
        db: AsyncSession
    ):
        return await UserRepository.get_all(db)

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ):

        user = await UserRepository.get_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ):

        user = await UserRepository.get_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password_hash"] = hash_password(
                update_data.pop("password")
            )

        updated_user = UserUpdate(**update_data)

        return await UserRepository.update(
            db,
            user,
            updated_user
        )

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int
    ):

        user = await UserRepository.get_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        await UserRepository.delete(
            db,
            user
        )

        return {
            "message": "User deleted successfully."
        }