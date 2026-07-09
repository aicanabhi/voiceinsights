from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate

from app.repositories.team_repository import TeamRepository
from app.repositories.organization_repository import OrganizationRepository


class TeamService:

    @staticmethod
    async def create_team(
        db: AsyncSession,
        team_data: TeamCreate
    ):

        # Check organization exists
        organization = await OrganizationRepository.get_by_id(
            db,
            team_data.organization_id
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        # Check duplicate team
        existing_team = await TeamRepository.get_by_name(
            db,
            team_data.name
        )

        if (
            existing_team
            and existing_team.organization_id == team_data.organization_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Team already exists in this organization."
            )

        team = Team(
            organization_id=team_data.organization_id,
            name=team_data.name,
            description=team_data.description,
        )

        return await TeamRepository.create(
            db,
            team
        )

    @staticmethod
    async def get_all_teams(
        db: AsyncSession
    ):
        return await TeamRepository.get_all(db)

    @staticmethod
    async def get_team_by_id(
        db: AsyncSession,
        team_id: int
    ):

        team = await TeamRepository.get_by_id(
            db,
            team_id
        )

        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        return team

    @staticmethod
    async def update_team(
        db: AsyncSession,
        team_id: int,
        team_data: TeamUpdate
    ):

        team = await TeamRepository.get_by_id(
            db,
            team_id
        )

        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        return await TeamRepository.update(
            db,
            team,
            team_data
        )

    @staticmethod
    async def delete_team(
        db: AsyncSession,
        team_id: int
    ):

        team = await TeamRepository.get_by_id(
            db,
            team_id
        )

        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        await TeamRepository.delete(
            db,
            team
        )

        return {
            "message": "Team deleted successfully."
        }