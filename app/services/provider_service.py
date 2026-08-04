from app.constants.provider_models import PROVIDER_MODELS
class ProviderService:

    @staticmethod
    async def get_providers():

        providers = []

        for provider, models in PROVIDER_MODELS.items():

            providers.append(
                {
                    "provider": provider,
                    "models": models
                }
            )

        return providers