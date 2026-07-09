from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.create_user(
        db,
        user
    )


@router.get(
    "/",
    response_model=list[UserResponse]
)
async def get_all_users(
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_user_by_id(
        db,
        user_id
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.update_user(
        db,
        user_id,
        user
    )


@router.delete(
    "/{user_id}"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.delete_user(
        db,
        user_id
    )