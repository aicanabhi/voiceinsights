from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    try:
        return await AuthService.register(
            db,
            user
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    try:
        return await AuthService.login(
            db,
            user
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )