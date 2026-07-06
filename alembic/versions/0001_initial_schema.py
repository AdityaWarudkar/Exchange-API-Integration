"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


role_enum = sa.Enum("admin", "trader", "viewer", name="role")
order_side_enum = sa.Enum("buy", "sell", name="orderside")
order_type_enum = sa.Enum("market", "limit", name="ordertype")
order_status_enum = sa.Enum("pending", "filled", "cancelled", "rejected", "expired", name="orderstatus")
position_status_enum = sa.Enum("open", "closed", name="positionstatus")
alert_severity_enum = sa.Enum("info", "warning", "critical", name="alertseverity")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "balances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("asset", sa.String(length=16), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("available", sa.Float(), nullable=False),
        sa.Column("locked", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "asset", name="uq_balance_user_asset"),
    )
    op.create_index(op.f("ix_balances_user_id"), "balances", ["user_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_order_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", order_side_enum, nullable=False),
        sa.Column("type", order_type_enum, nullable=False),
        sa.Column("status", order_status_enum, nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("filled_quantity", sa.Float(), nullable=False),
        sa.Column("average_fill_price", sa.Float(), nullable=True),
        sa.Column("fee", sa.Float(), nullable=False),
        sa.Column("error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_client_order_id"), "orders", ["client_order_id"], unique=True)
    op.create_index(op.f("ix_orders_symbol"), "orders", ["symbol"], unique=False)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"], unique=False)

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("status", position_status_enum, nullable=False),
        sa.Column("entry_price", sa.Float(), nullable=False),
        sa.Column("current_price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("leverage", sa.Float(), nullable=False),
        sa.Column("margin", sa.Float(), nullable=False),
        sa.Column("liquidation_price", sa.Float(), nullable=True),
        sa.Column("realized_pnl", sa.Float(), nullable=False),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False),
        sa.Column("roi", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_positions_symbol"), "positions", ["symbol"], unique=False)
    op.create_index(op.f("ix_positions_user_id"), "positions", ["user_id"], unique=False)

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("fee", sa.Float(), nullable=False),
        sa.Column("realized_pnl", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trades_order_id"), "trades", ["order_id"], unique=False)
    op.create_index(op.f("ix_trades_symbol"), "trades", ["symbol"], unique=False)

    op.create_table(
        "portfolio",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_balance", sa.Float(), nullable=False),
        sa.Column("available_balance", sa.Float(), nullable=False),
        sa.Column("locked_balance", sa.Float(), nullable=False),
        sa.Column("today_profit", sa.Float(), nullable=False),
        sa.Column("today_loss", sa.Float(), nullable=False),
        sa.Column("total_trades", sa.Integer(), nullable=False),
        sa.Column("winning_percentage", sa.Float(), nullable=False),
        sa.Column("open_positions", sa.Integer(), nullable=False),
        sa.Column("closed_positions", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_user_id"), "portfolio", ["user_id"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("severity", alert_severity_enum, nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("payload", sa.String(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_type"), "alerts", ["type"], unique=False)

    op.create_table(
        "exchange_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=False),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exchange_logs_exchange"), "exchange_logs", ["exchange"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_exchange_logs_exchange"), table_name="exchange_logs")
    op.drop_table("exchange_logs")
    op.drop_index(op.f("ix_alerts_type"), table_name="alerts")
    op.drop_table("alerts")
    op.drop_index(op.f("ix_portfolio_user_id"), table_name="portfolio")
    op.drop_table("portfolio")
    op.drop_index(op.f("ix_trades_symbol"), table_name="trades")
    op.drop_index(op.f("ix_trades_order_id"), table_name="trades")
    op.drop_table("trades")
    op.drop_index(op.f("ix_positions_user_id"), table_name="positions")
    op.drop_index(op.f("ix_positions_symbol"), table_name="positions")
    op.drop_table("positions")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_symbol"), table_name="orders")
    op.drop_index(op.f("ix_orders_client_order_id"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_balances_user_id"), table_name="balances")
    op.drop_table("balances")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    alert_severity_enum.drop(op.get_bind(), checkfirst=True)
    position_status_enum.drop(op.get_bind(), checkfirst=True)
    order_status_enum.drop(op.get_bind(), checkfirst=True)
    order_type_enum.drop(op.get_bind(), checkfirst=True)
    order_side_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)

