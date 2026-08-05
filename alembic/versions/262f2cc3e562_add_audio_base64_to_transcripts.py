"""add_audio_base64_to_transcripts

Revision ID: 262f2cc3e562
Revises: a7a8de6d5716
Create Date: 2026-08-05 13:04:53.892808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '262f2cc3e562'
down_revision: Union[str, Sequence[str], None] = 'a7a8de6d5716'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.alter_column(
        "transcripts",
        "base64",
        new_column_name="audio_base64"
    )


def downgrade():

    op.alter_column(
        "transcripts",
        "audio_base64",
        new_column_name="base64"
    )
