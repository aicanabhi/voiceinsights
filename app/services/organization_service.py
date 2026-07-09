from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)


class OrganizationService:

    @staticmethod
    async def create_organization(
        db: AsyncSession,
        data: OrganizationCreate,
    ):

        existing = await OrganizationRepository.get_by_email(
            db,
            data.email,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Organization already exists."
            )

        organization = Organization(
            name=data.name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            website=data.website,
            industry=data.industry,
        )

        return await OrganizationRepository.create(
            db,
            organization,
        )

    @staticmethod
    async def get_all_organizations(
        db: AsyncSession,
    ):
        return await OrganizationRepository.get_all(db)

    @staticmethod
    async def get_organization(
        db: AsyncSession,
        organization_id: int,
    ):

        organization = await OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        return organization

    @staticmethod
    async def update_organization(
        db: AsyncSession,
        organization_id: int,
        data: OrganizationUpdate,
    ):

        organization = await OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(organization, key, value)

        await db.commit()
        await db.refresh(organization)

        return organization

    @staticmethod
    async def delete_organization(
        db: AsyncSession,
        organization_id: int,
    ):

        organization = await OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        await OrganizationRepository.delete(
            db,
            organization,
        )

        return {
            "message": "Organization deleted successfully."
        }