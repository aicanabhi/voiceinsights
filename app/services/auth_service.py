from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.core.security import verify_password
from app.core.jwt import create_access_token


class AuthService:

    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str
    ):

        user = await UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            raise Exception("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash
        ):
            raise Exception("Invalid email or password")

        if not user.is_active:
            raise Exception("User is inactive")

        token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role.value
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role.value,
                "organization_id": user.organization_id,
                "team_id": user.team_id,
                "is_active": user.is_active
            }
        }