"""media job status: queue columns + backfill

Replaces media.upload_status (which only ever held the literal "UPLOADED")
with a real job lifecycle, so the media table can act as the transcription
work queue and report progress.

Backfill: rows that already have a transcript are COMPLETED; the rest were
never processed and are marked FAILED with a note, so the worker does not
re-run months of old uploads and re-bill the provider APIs.

Revision ID: c7d24e8b1f05
Revises: b3f1c9a24d17
Create Date: 2026-08-10

"""
from alembic import op
import sqlalchemy as sa


revision = "c7d24e8b1f05"
down_revision = "b3f1c9a24d17"
branch_labels = None
depends_on = None


MEDIA_STATUS = sa.Enum(
    "PENDING",
    "PROCESSING",
    "TRANSCRIBED",
    "COMPLETED",
    "FAILED",
    name="mediastatus",
)


def upgrade() -> None:

    bind = op.get_bind()
    MEDIA_STATUS.create(bind, checkfirst=True)

    op.add_column(
        "media",
        sa.Column("status", MEDIA_STATUS, nullable=True),
    )
    op.add_column(
        "media",
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "media",
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "media",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "media",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Already transcribed -> COMPLETED
    op.execute(
        """
        UPDATE media
           SET status = 'COMPLETED',
               completed_at = created_at
         WHERE EXISTS (
               SELECT 1 FROM transcripts t WHERE t.media_id = media.id
         )
        """
    )

    # Never processed -> FAILED, with a reason instead of a silent gap
    op.execute(
        """
        UPDATE media
           SET status = 'FAILED',
               error_message = 'migrated: never processed by a worker'
         WHERE status IS NULL
        """
    )

    op.alter_column("media", "status", nullable=False)

    op.create_index(
        "ix_media_status_created_at",
        "media",
        ["status", "created_at"],
    )

    op.drop_column("media", "upload_status")


def downgrade() -> None:

    op.add_column(
        "media",
        sa.Column(
            "upload_status",
            sa.String(length=30),
            nullable=True,
            server_default="UPLOADED",
        ),
    )
    op.execute("UPDATE media SET upload_status = 'UPLOADED'")

    op.drop_index("ix_media_status_created_at", table_name="media")

    for column in (
        "completed_at",
        "started_at",
        "attempts",
        "error_message",
        "status",
    ):
        op.drop_column("media", column)

    MEDIA_STATUS.drop(op.get_bind(), checkfirst=True)
