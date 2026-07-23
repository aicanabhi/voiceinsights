from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

from app.services.organization_service import OrganizationService

from app.core.dependencies import (
    get_current_user,
    require_roles,
)

from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# ---------------------------------------
# Create Organization
# Only Super Admin
# ---------------------------------------
@router.post(
    "/",
    response_model=OrganizationResponse
)
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN)
    ),
):
    return await OrganizationService.create_organization(
        db=db,
        data=organization,
    )


# ---------------------------------------
# Get All Organizations
# Only Super Admin
# ---------------------------------------
@router.get(
    "/",
    response_model=list[OrganizationResponse]
)
async def get_all_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN)
    ),
):
    return await OrganizationService.get_all_organizations(db)


# ---------------------------------------
# Get Organization
# Super Admin + Org Admin
# ---------------------------------------
@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def get_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.ORG_ADMIN,
        )
    ),
):
    return await OrganizationService.get_organization(
        db=db,
        organization_id=organization_id,
        current_user=current_user,
    )


# ---------------------------------------
# Update Organization
# Super Admin + Org Admin
# ---------------------------------------
@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def update_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.ORG_ADMIN,
        )
    ),
):
    return await OrganizationService.update_organization(
        db=db,
        organization_id=organization_id,
        data=organization,
        current_user=current_user,
    )


# ---------------------------------------
# Delete Organization
# Only Super Admin
# ---------------------------------------
@router.delete(
    "/{organization_id}"
)
async def delete_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN)
    ),
):
    return await OrganizationService.delete_organization(
        db=db,
        organization_id=organization_id,
    )