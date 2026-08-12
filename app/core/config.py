from typing import Optional

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
    MONGO_URL: str

    DEEPGRAM_API_KEY: str
    ELEVENLABS_API_KEY: str
    CARTESIA_API_KEY: str
    GROQ_API_KEY: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # CORS -- comma separated list of frontend origins allowed to call the API.
    # Defaults cover the Vite dev server on both loopback spellings.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Transcription worker
    # Run the poller inside the API process (handy in dev). In production
    # leave this false and run `python -m app.worker` as its own process.
    RUN_WORKER_IN_APP: bool = False
    WORKER_POLL_SECONDS: float = 5.0
    WORKER_CONCURRENCY: int = 2
    WORKER_MAX_ATTEMPTS: int = 3

    # Super Admin seed (used only by app/scripts/create_super_admin.py)
    SUPER_ADMIN_EMAIL: Optional[str] = None
    SUPER_ADMIN_PASSWORD: Optional[str] = None
    SUPER_ADMIN_NAME: str = "Super Admin"
    SUPER_ADMIN_PHONE: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def CORS_ORIGIN_LIST(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.DATABASE_NAME}"
        )

    @property
    def SYNC_DATABASE_URL(self):
        return (
            f"postgresql+psycopg2://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.DATABASE_NAME}"
        )


settings = Settings()