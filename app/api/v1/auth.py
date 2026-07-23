from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.change_password import ChangePasswordRequest
from app.models.enums import UserRole
from app.core.security import verify_password, hash_password
from app.db.session import get_db
from app.services.auth_service import AuthService
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
    try:

        return await AuthService.login(
            db=db,
            email=form_data.username,
            password=form_data.password
        )

    except Exception as e:
        print("LOGIN ERROR:", repr(e))

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can change password."
        )

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

    await db.commit()

    return {
        "message": "Password changed successfully"
    }