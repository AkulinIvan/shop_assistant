"""add unknown_topics"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "unknown_topics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("pattern", sa.String(255), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("unknown_topics")