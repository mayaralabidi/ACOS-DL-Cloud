"""initial schema

Revision ID: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("label", sa.String, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("category", sa.String, server_default="general"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("status", sa.String, server_default="processing"),
        sa.Column("video_path", sa.String, nullable=True),
        sa.Column("receipt_raw", sa.JSON, nullable=True),
        sa.Column("receipt_final", sa.JSON, nullable=True),
        sa.Column("total", sa.Float, server_default="0.0"),
        sa.Column("frame_count", sa.Integer, server_default="0"),
        sa.Column("model_version", sa.String, server_default="unknown"),
        sa.Column("error", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "receipt_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String, sa.ForeignKey("sessions.id", ondelete="CASCADE")),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Float, nullable=False),
        sa.Column("subtotal", sa.Float, nullable=False),
        sa.Column("is_override", sa.Boolean, server_default="false"),
    )

    op.create_index("ix_sessions_created_at", "sessions", ["created_at"])
    op.create_index("ix_receipt_items_session_id", "receipt_items", ["session_id"])


def downgrade():
    op.drop_table("receipt_items")
    op.drop_table("sessions")
    op.drop_table("products")