from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.provider import ProviderModels
from app.services.provider_service import ProviderService

router = APIRouter(
    prefix="/providers",
    tags=["Providers"]
)


@router.get(
    "/",
    response_model=list[ProviderModels],
    dependencies=[Depends(get_current_user)]
)
async def get_providers():

    return await ProviderService.get_providers()