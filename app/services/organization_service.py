from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.models.enums import UserRole

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

        existing = await OrganizationRepository.get_by_domain(
            db,
            data.domain,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Organization domain already exists."
            )

        organization = Organization(
            name=data.name,
            phone=data.phone,
            address=data.address,
            domain=data.domain,
            website=data.website,
            is_active=True,
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
        current_user: User,
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

        if (
            current_user.role == UserRole.ORG_ADMIN
            and current_user.organization_id != organization.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can access only your organization."
            )

        return organization

    @staticmethod
    async def update_organization(
        db: AsyncSession,
        organization_id: int,
        data: OrganizationUpdate,
        current_user: User,
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

        if (
            current_user.role == UserRole.ORG_ADMIN
            and current_user.organization_id != organization.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can update only your organization."
            )

        return await OrganizationRepository.update(
            db,
            organization,
            data,
        )

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