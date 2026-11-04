"""init schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
    )
    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("intent_id", sa.Integer,
                  sa.ForeignKey("intents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pattern", sa.String(255), nullable=False),
        sa.Column("weight", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_table(
        "facts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("intent_id", sa.Integer,
                  sa.ForeignKey("intents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("template", sa.Text, nullable=False),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_table(
        "fact_variables",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("fact_id", sa.Integer,
                  sa.ForeignKey("facts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
    )
    op.create_table(
        "guardrail_rules",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("pattern", sa.String(512), nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="1"),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("intent", sa.String(64), nullable=True),
        sa.Column("ts", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    for t in ["audit_log", "guardrail_rules", "fact_variables",
              "facts", "keywords", "intents"]:
        op.drop_table(t)