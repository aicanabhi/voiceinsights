from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.schemas.team import TeamUpdate


class TeamRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        team: Team
    ):
        db.add(team)
        await db.commit()
        await db.refresh(team)
        return team

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Team)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        team_id: int
    ):
        result = await db.execute(
            select(Team).where(
                Team.id == team_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str
    ):
        result = await db.execute(
            select(Team).where(
                Team.name == name
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession,
        team: Team,
        data: TeamUpdate
    ):
        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(team, key, value)

        await db.commit()
        await db.refresh(team)

        return team

    @staticmethod
    async def delete(
        db: AsyncSession,
        team: Team
    ):
        await db.delete(team)
        await db.commit()