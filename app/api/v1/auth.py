from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.change_password import ChangePasswordRequest
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.login(
        db=db,
        email=form_data.username,
        password=form_data.password
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.change_password(
        db=db,
        current_user=current_user,
        request=request
    )
