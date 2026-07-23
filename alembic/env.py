from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

from app.core.config import settings
from app.db.base import Base

from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.models.media import Media
from app.models.transcript import Transcript
from app.models.analysis import Analysis
from app.models.transcript_segment import TranscriptSegment

target_metadata = Base.metadata

config = context.config

SYNC_DATABASE_URL = (
    f"postgresql://"
    f"{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}"
    f"/{settings.DATABASE_NAME}"
)

config.set_main_option(
    "sqlalchemy.url",
    SYNC_DATABASE_URL
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():

    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    connectable = create_engine(
        SYNC_DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()