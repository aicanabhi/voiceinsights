from app.constants.provider_models import PROVIDER_MODELS


class ProviderRepository:

    @staticmethod
    async def get_models(provider: str):

        return PROVIDER_MODELS.get(
            provider.upper(),
            []
        )