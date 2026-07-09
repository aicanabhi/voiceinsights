from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from app.repositories.user_repository import UserRepository

from app.schemas.user import (
    UserCreate,
    UserLogin
)

from app.core.security import (
    hash_password,
    verify_password
)

from app.core.jwt import create_access_token


class AuthService:

    @staticmethod
    async def register(
        db: AsyncSession,
        data: UserCreate
    ):

        existing = await UserRepository.get_by_email(
            db,
            data.email
        )

        if existing:
            raise Exception("Email already exists")

        user = User(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=data.role,
            organization_id=data.organization_id,
            team_id=data.team_id,
        )

        return await UserRepository.create(
            db,
            user
        )

    @staticmethod
    async def login(
        db: AsyncSession,
        data: UserLogin
    ):

        user = await UserRepository.get_by_email(
            db,
            data.email
        )

        if not user:
            raise Exception("Invalid credentials")

        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise Exception("Invalid credentials")

        token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role.value
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }