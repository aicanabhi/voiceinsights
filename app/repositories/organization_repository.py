from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
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
    async def get_by_email(
        db: AsyncSession,
        email: str
    ):
        result = await db.execute(
            select(Organization).where(
                Organization.email == email
            )
        )
        return result.scalar_one_or_none()

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