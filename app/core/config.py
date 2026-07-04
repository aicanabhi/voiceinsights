from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # AI APIs
    OPENAI_API_KEY: str = ""
    DEEPGRAM_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.DATABASE_NAME}"
        )


settings = Settings()