from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse
)

from app.services.team_service import TeamService

from app.core.dependencies import (
    get_current_user,
    require_roles
)

from app.models.user import User
from app.models.enums import UserRole


router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.post(
    "/",
    response_model=TeamResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN
            )
        )
    ]
)
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await TeamService.create_team(
        db=db,
        team_data=team,
        current_user=current_user
    )


@router.get(
    "/",
    response_model=list[TeamResponse]
)
async def get_all_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await TeamService.get_all_teams(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{team_id}",
    response_model=TeamResponse
)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await TeamService.get_team_by_id(
        db=db,
        team_id=team_id,
        current_user=current_user
    )


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN
            )
        )
    ]
)
async def update_team(
    team_id: int,
    team: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await TeamService.update_team(
        db=db,
        team_id=team_id,
        team_data=team,
        current_user=current_user
    )


@router.delete(
    "/{team_id}",
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN
            )
        )
    ]
)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await TeamService.delete_team(
        db=db,
        team_id=team_id,
        current_user=current_user
    )