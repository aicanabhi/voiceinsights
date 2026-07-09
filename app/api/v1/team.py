from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.services.team_service import TeamService

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.post("/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db)
):
    return await TeamService.create_team(db, team)


@router.get("/", response_model=list[TeamResponse])
async def get_all_teams(
    db: AsyncSession = Depends(get_db)
):
    return await TeamService.get_all_teams(db)


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TeamService.get_team_by_id(
        db,
        team_id
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team: TeamUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await TeamService.update_team(
        db,
        team_id,
        team
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TeamService.delete_team(
        db,
        team_id
    )