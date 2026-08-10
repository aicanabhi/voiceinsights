"""unique team name per org, drop orphan speaker_segments column

Two leftovers:

* transcripts.speaker_segments (JSON) was added by 63f81f20d2ce but the model
  never had the field -- speaker data lives in the transcript_segments table.
* teams had no uniqueness, so the duplicate check in TeamService could not be
  trusted and two orgs sharing a team name made the lookup return two rows.

Revision ID: d8e5a1c73b92
Revises: c7d24e8b1f05
Create Date: 2026-08-11

"""
from alembic import op
import sqlalchemy as sa


revision = "d8e5a1c73b92"
down_revision = "c7d24e8b1f05"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # Column was never mapped, so nothing in the app can be reading it.
    op.drop_column("transcripts", "speaker_segments")

    # Collapse any duplicates that slipped in before the constraint existed:
    # keep the oldest team, move its members over, drop the rest.
    op.execute(
        """
        UPDATE users u
           SET team_id = keep.keep_id
          FROM (
                SELECT t.id AS dup_id,
                       MIN(t2.id) AS keep_id
                  FROM teams t
                  JOIN teams t2
                    ON t2.organization_id = t.organization_id
                   AND t2.name = t.name
                 GROUP BY t.id
                HAVING MIN(t2.id) <> t.id
               ) AS keep
         WHERE u.team_id = keep.dup_id
        """
    )

    op.execute(
        """
        DELETE FROM teams t
         WHERE EXISTS (
               SELECT 1 FROM teams t2
                WHERE t2.organization_id = t.organization_id
                  AND t2.name = t.name
                  AND t2.id < t.id
         )
        """
    )

    op.create_unique_constraint(
        "uq_teams_organization_name",
        "teams",
        ["organization_id", "name"],
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_teams_organization_name",
        "teams",
        type_="unique",
    )

    op.add_column(
        "transcripts",
        sa.Column("speaker_segments", sa.JSON(), nullable=True),
    )
