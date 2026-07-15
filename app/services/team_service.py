from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.user import User
from app.models.enums import UserRole

from app.schemas.team import TeamCreate, TeamUpdate

from app.repositories.team_repository import TeamRepository
from app.repositories.organization_repository import OrganizationRepository


class TeamService:

    @staticmethod
    async def create_team(
        db: AsyncSession,
        team_data: TeamCreate,
        current_user: User
    ):

        # -------------------------
        # Role Permission
        # -------------------------

        if current_user.role == UserRole.SUPER_ADMIN:

            pass

        elif current_user.role == UserRole.ORG_ADMIN:

            if (
                team_data.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can create teams only in your organization."
                )

        else:

            raise HTTPException(
                status_code=403,
                detail="Permission denied."
            )

        # -------------------------
        # Organization Exists
        # -------------------------

        organization = await OrganizationRepository.get_by_id(
            db,
            team_data.organization_id
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        # -------------------------
        # Duplicate Team
        # -------------------------

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
                detail="Team already exists."
            )

        team = Team(
            organization_id=team_data.organization_id,
            name=team_data.name,
            description=team_data.description,
            is_active=True
        )

        return await TeamRepository.create(
            db,
            team
        )

    @staticmethod
    async def get_all_teams(
        db: AsyncSession,
        current_user: User
    ):

        teams = await TeamRepository.get_all(db)

        if current_user.role == UserRole.SUPER_ADMIN:
            return teams

        if current_user.role == UserRole.ORG_ADMIN:

            return [
                team
                for team in teams
                if team.organization_id == current_user.organization_id
            ]

        if current_user.role == UserRole.TEAM_LEAD:

            return [
                team
                for team in teams
                if team.id == current_user.team_id
            ]

        raise HTTPException(
            status_code=403,
            detail="Permission denied."
        )

    @staticmethod
    async def get_team_by_id(
        db: AsyncSession,
        team_id: int,
        current_user: User
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

        if current_user.role == UserRole.SUPER_ADMIN:
            return team

        if current_user.role == UserRole.ORG_ADMIN:

            if (
                team.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied."
                )

            return team

        if current_user.role == UserRole.TEAM_LEAD:

            if (
                team.id
                != current_user.team_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied."
                )

            return team

        raise HTTPException(
            status_code=403,
            detail="Permission denied."
        )

    @staticmethod
    async def update_team(
        db: AsyncSession,
        team_id: int,
        team_data: TeamUpdate,
        current_user: User
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

        if current_user.role == UserRole.SUPER_ADMIN:

            pass

        elif current_user.role == UserRole.ORG_ADMIN:

            if (
                team.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied."
                )

        else:

            raise HTTPException(
                status_code=403,
                detail="Permission denied."
            )

        return await TeamRepository.update(
            db,
            team,
            team_data
        )

    @staticmethod
    async def delete_team(
        db: AsyncSession,
        team_id: int,
        current_user: User
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

        if current_user.role == UserRole.SUPER_ADMIN:

            pass

        elif current_user.role == UserRole.ORG_ADMIN:

            if (
                team.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied."
                )

        else:

            raise HTTPException(
                status_code=403,
                detail="Permission denied."
            )

        await TeamRepository.delete(
            db,
            team
        )

        return {
            "message": "Team deleted successfully."
        }