from fastapi import APIRouter

from app.schemas.provider import ProviderModels
from app.services.provider_service import ProviderService

router = APIRouter(
    prefix="/providers",
    tags=["Providers"]
)


@router.get(
    "/",
    response_model=list[ProviderModels]
)
async def get_providers():

    return await ProviderService.get_providers()