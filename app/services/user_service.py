from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository

from app.core.security import (
    verify_password,
    hash_password
)
from app.models.enums import UserRole


class UserService:

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
        current_user: User
    ):

        existing_user = await UserRepository.get_by_email(
            db,
            user_data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

        if current_user.role == UserRole.SUPER_ADMIN:

            allowed_roles = [
                UserRole.ORG_ADMIN
            ]

        elif current_user.role == UserRole.ORG_ADMIN:

            allowed_roles = [
                UserRole.TEAM_LEAD,
                UserRole.AGENT
            ]

            if (
                user_data.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can create users only in your organization."
                )

        elif current_user.role == UserRole.TEAM_LEAD:

            allowed_roles = [
                UserRole.AGENT
            ]

            if (
                user_data.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid organization."
                )

            if (
                user_data.team_id
                != current_user.team_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can create agents only in your own team."
                )

        else:

            raise HTTPException(
                status_code=403,
                detail="You are not allowed to create users."
            )

        if user_data.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail=f"You cannot create {user_data.role.value}"
            )

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
            password_hash=hash_password(
                user_data.password
            ),
            role=user_data.role,
            organization_id=user_data.organization_id,
            team_id=user_data.team_id,
            is_active=True
        )

        return await UserRepository.create(
            db,
            user
        )

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        current_user: User
    ):
        users = await UserRepository.get_all(db)
        
        if current_user.role == UserRole.SUPER_ADMIN:
            return users

        if current_user.role == UserRole.ORG_ADMIN:
            return [
                user for user in users
                if user.organization_id == current_user.organization_id
            ]
        
        if current_user.role == UserRole.TEAM_LEAD:
            return [
                user for user in users
                if user.team_id == current_user.team_id
            ]
        return [
            current_user
        ]

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int,
        current_user: User
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

        if current_user.role == UserRole.SUPER_ADMIN:
            return user

        if current_user.role == UserRole.ORG_ADMIN:
            if user.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can access only users in your organization."
                )
            return user
        
        if current_user.role == UserRole.TEAM_LEAD:
            if user.team_id != current_user.team_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can access only users in your team."
                )
            return user

        if current_user.id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can access only your own user data."
            )

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
        current_user: User
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
        if current_user.role == UserRole.SUPER_ADMIN:
            pass

        elif current_user.role == UserRole.ORG_ADMIN:
            if user.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can update only users in your organization."
                )
        elif current_user.role == UserRole.TEAM_LEAD:
            if user.team_id != current_user.team_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can update only users in your team."
                )
        else:
            if current_user.id != user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can update only your own user data."
                )

        return await UserRepository.update(
            db,
            user,
            user_data
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

        if current_user.role == UserRole.SUPER_ADMIN:
            pass

        elif current_user.role == UserRole.ORG_ADMIN:
            if user.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can delete only users in your organization."
                )
        elif current_user.role == UserRole.TEAM_LEAD:
            if user.team_id != current_user.team_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied"
                )
        else:
            raise HTTPException(
                status_code=403,
                detail="Agents cannot delte users."
            )

        await UserRepository.delete(
            db,
            user
        )

        return {
            "message": "User deleted successfully."
        }

    @staticmethod
    async def change_password(
        db: AsyncSession,
        current_user: User,
        request
    ):

        if not verify_password(
            request.current_password,
            current_user.password_hash
        ):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect."
            )

        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Passwords do not match."
            )

        current_user.password_hash = hash_password(
            request.new_password
        )

        return await UserRepository.change_password(
            db,
            current_user
        )