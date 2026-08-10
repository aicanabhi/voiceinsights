"""drop audio_base64 from transcripts

The column stored a base64 copy of audio that already lives on disk and is
referenced by media.file_path. No API ever returned it -- TranscriptResponse
does not expose the field -- so it was write-only bloat of ~1.33x every
uploaded file. Audio is now served by GET /media/{media_id}/audio.

Revision ID: b3f1c9a24d17
Revises: 63f81f20d2ce
Create Date: 2026-08-10

"""
from alembic import op
import sqlalchemy as sa


revision = "b3f1c9a24d17"
down_revision = "63f81f20d2ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("transcripts", "audio_base64")


def downgrade() -> None:
    # Recreated empty: the original blobs are not recoverable from here, but
    # the audio itself is still on disk under media.file_path.
    op.add_column(
        "transcripts",
        sa.Column("audio_base64", sa.Text(), nullable=True),
    )
