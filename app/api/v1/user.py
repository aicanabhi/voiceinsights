from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

from app.services.user_service import UserService

from app.core.dependencies import (
    get_current_user,
    require_roles
)
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN,
                UserRole.TEAM_LEAD
            )
        )
    ]
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.create_user(
        db=db,
        user_data=user,
        current_user=current_user
    )


@router.get(
    "/",
    response_model=list[UserResponse]
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.get_all_users(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.get_user_by_id(
        db,
        user_id,
        current_user=current_user
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.update_user(
        db,
        user_id,
        user,
        current_user=current_user
    )


@router.delete(
    "/{user_id}"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await UserService.delete_user(
        db,
        user_id=user_id,
        current_user=current_user
    )
