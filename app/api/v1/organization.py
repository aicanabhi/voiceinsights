from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

from app.services.organization_service import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


@router.post(
    "/",
    response_model=OrganizationResponse
)
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationService.create_organization(
        db,
        organization
    )


@router.get(
    "/",
    response_model=list[OrganizationResponse]
)
async def get_organizations(
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationService.get_all_organizations(db)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def get_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationService.get_organization(
        db,
        organization_id
    )


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def update_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationService.update_organization(
        db,
        organization_id,
        organization
    )


@router.delete(
    "/{organization_id}"
)
async def delete_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationService.delete_organization(
        db,
        organization_id
    )