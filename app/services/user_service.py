from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.change_password import ChangePasswordRequest
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
    def _ensure_can_manage(
        current_user: User,
        user: User,
        action: str,
        allow_self: bool = False
    ):
        """Shared authorization guard for update_user / delete_user.

        Scope is matched on organization_id / team_id, so a NULL scope must
        never count as a match -- an ORG_ADMIN with no organization would
        otherwise match the SUPER_ADMIN row, which is unscoped by design.
        """

        if user.role == UserRole.SUPER_ADMIN:

            if current_user.role != UserRole.SUPER_ADMIN:
                raise HTTPException(
                    status_code=403,
                    detail=f"You cannot {action} a Super Admin."
                )

            return

        if current_user.role == UserRole.SUPER_ADMIN:
            return

        if current_user.role == UserRole.ORG_ADMIN:

            if (
                current_user.organization_id is None
                or user.organization_id != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"You can {action} only users in your organization."
                )

            return

        if current_user.role == UserRole.TEAM_LEAD:

            if (
                current_user.team_id is None
                or user.team_id != current_user.team_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"You can {action} only users in your team."
                )

            return

        if not allow_self or current_user.id != user.id:
            raise HTTPException(
                status_code=403,
                detail=f"You can {action} only your own user data."
            )

    @staticmethod
    async def _ensure_not_last_super_admin(
        db: AsyncSession,
        user: User,
        action: str
    ):
        """Losing the last active Super Admin locks everyone out for good --
        the role cannot be granted through the API, only by the seed script.
        """

        if user.role != UserRole.SUPER_ADMIN:
            return

        remaining = await UserRepository.count_active_by_role(
            db,
            UserRole.SUPER_ADMIN
        )

        if remaining <= 1:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot {action} the only active Super Admin."
            )

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

            if current_user.organization_id is None:
                raise HTTPException(
                    status_code=403,
                    detail="Your account is not linked to an organization."
                )

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
                current_user.organization_id is None
                or current_user.team_id is None
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Your account is not linked to a team."
                )

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

        # Every non-super-admin must be scoped. An unscoped user cannot be
        # governed by any permission check and would collide with the
        # SUPER_ADMIN row, which is the only account allowed to be unscoped.

        if user_data.organization_id is None:
            raise HTTPException(
                status_code=400,
                detail=f"organization_id is required for {user_data.role.value}."
            )

        if (
            user_data.role in (UserRole.TEAM_LEAD, UserRole.AGENT)
            and user_data.team_id is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"team_id is required for {user_data.role.value}."
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
        UserService._ensure_can_manage(
            current_user,
            user,
            "update",
            allow_self=True
        )

        if user_data.is_active is False:

            if current_user.id == user.id:
                raise HTTPException(
                    status_code=400,
                    detail="You cannot deactivate your own account."
                )

            await UserService._ensure_not_last_super_admin(
                db,
                user,
                "deactivate"
            )

        return await UserRepository.update(
            db,
            user,
            user_data
        )

    @staticmethod
    async def delete_user(
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

        UserService._ensure_can_manage(
            current_user,
            user,
            "delete"
        )

        if current_user.id == user.id:
            raise HTTPException(
                status_code=400,
                detail="You cannot delete your own account."
            )

        await UserService._ensure_not_last_super_admin(
            db,
            user,
            "delete"
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
        request: ChangePasswordRequest
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

        if request.new_password == request.current_password:
            raise HTTPException(
                status_code=400,
                detail="New password must be different from the current one."
            )

        current_user.password_hash = hash_password(
            request.new_password
        )

        await UserRepository.change_password(
            db,
            current_user
        )

        return {
            "message": "Password changed successfully"
        }