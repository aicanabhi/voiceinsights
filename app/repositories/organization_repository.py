from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.schemas.organization import OrganizationUpdate


class OrganizationRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        organization: Organization
    ):
        db.add(organization)
        await db.commit()
        await db.refresh(organization)
        return organization

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Organization)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        organization_id: int
    ):
        result = await db.execute(
            select(Organization).where(
                Organization.id == organization_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_domain(
        db: AsyncSession,
        domain: str
    ):
        result = await db.execute(
            select(Organization).where(
                Organization.domain == domain
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def count_cascade(
        db: AsyncSession,
        organization_id: int
    ):
        """Rows that deleting this organization will take with it."""

        users = await db.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.organization_id == organization_id
            )
        )

        teams = await db.execute(
            select(func.count())
            .select_from(Team)
            .where(
                Team.organization_id == organization_id
            )
        )

        return users.scalar_one(), teams.scalar_one()

    @staticmethod
    async def update(
        db: AsyncSession,
        organization: Organization,
        data: OrganizationUpdate
    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                organization,
                key,
                value
            )

        await db.commit()
        await db.refresh(
            organization
        )

        return organization

    @staticmethod
    async def delete(
        db: AsyncSession,
        organization: Organization
    ):
        await db.delete(
            organization
        )

        await db.commit()