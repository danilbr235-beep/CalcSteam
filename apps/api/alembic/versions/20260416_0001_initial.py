"""initial schema

Revision ID: 20260416_0001
Revises:
Create Date: 2026-04-16
"""

from alembic import op
import sqlalchemy as sa

revision = "20260416_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.Enum("admin", "operator", "viewer", name="userrole"), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table("supplier_code_types", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("currency", sa.String(3), nullable=False), sa.Column("face_value", sa.Float(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("purchase_batches", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("supplier_name", sa.String(255), nullable=False), sa.Column("purchased_at", sa.DateTime(), nullable=False), sa.Column("note", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("sell_nominals", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("currency", sa.String(3), nullable=False), sa.Column("nominal", sa.Float(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("pricing_configs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("marketplace_fee_percent", sa.Float(), nullable=False), sa.Column("risk_reserve_percent", sa.Float(), nullable=False), sa.Column("min_profit_rub", sa.Float(), nullable=False), sa.Column("target_profit_percent", sa.Float(), nullable=False), sa.Column("rounding_rule", sa.String(64), nullable=False), sa.Column("max_codes_per_order", sa.Integer(), nullable=False), sa.Column("underfill_tolerance_percent", sa.Float(), nullable=False), sa.Column("overfill_tolerance_percent", sa.Float(), nullable=False), sa.Column("ad_allocation_mode", sa.String(64), nullable=False), sa.Column("default_ad_cost_per_sale", sa.Float(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("promotion_cost_rules", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("currency", sa.String(3), nullable=False), sa.Column("nominal_from", sa.Float(), nullable=False), sa.Column("nominal_to", sa.Float(), nullable=False), sa.Column("ad_cost_rub", sa.Float(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("fx_rates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("from_currency", sa.String(3), nullable=False), sa.Column("to_currency", sa.String(3), nullable=False), sa.Column("rate", sa.Float(), nullable=False), sa.Column("source", sa.String(64), nullable=False), sa.Column("fetched_at", sa.DateTime(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_fx_rates_pair_fetched", "fx_rates", ["from_currency", "to_currency", sa.text("fetched_at DESC")], unique=False)

    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("external_ref", sa.String(128), nullable=False), sa.Column("sell_nominal_id", sa.Integer(), sa.ForeignKey("sell_nominals.id"), nullable=False), sa.Column("status", sa.Enum("new", "reserved", "fulfilled", "problem", "completed", name="orderstatus"), nullable=False), sa.Column("expected_revenue_rub", sa.Float(), nullable=False), sa.Column("manual_review", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_orders_external_ref", "orders", ["external_ref"], unique=True)
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)

    op.create_table("code_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("batch_id", sa.Integer(), sa.ForeignKey("purchase_batches.id"), nullable=False), sa.Column("supplier_code_type_id", sa.Integer(), sa.ForeignKey("supplier_code_types.id"), nullable=False), sa.Column("encrypted_code", sa.Text(), nullable=False), sa.Column("masked_code", sa.String(32), nullable=False), sa.Column("purchase_cost_rub", sa.Float(), nullable=False), sa.Column("status", sa.Enum("new", "reserved", "sent", "redeemed", "problem", "archived", name="codestatus"), nullable=False), sa.Column("reserved_until", sa.DateTime(), nullable=True), sa.Column("reserved_order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_code_items_status", "code_items", ["status"], unique=False)

    op.create_table("price_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("sell_nominal_id", sa.Integer(), sa.ForeignKey("sell_nominals.id"), nullable=False), sa.Column("recommended_price_rub", sa.Float(), nullable=False), sa.Column("best_combo", sa.JSON(), nullable=False), sa.Column("estimated_profit_rub", sa.Float(), nullable=False), sa.Column("margin_percent", sa.Float(), nullable=False), sa.Column("status", sa.Enum("ok", "low_margin", "loss", "no_combo", "stale_rate", "low_stock", "manual_review", name="itemriskstatus"), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_price_snapshots_nominal_created", "price_snapshots", ["sell_nominal_id", sa.text("created_at DESC")], unique=False)

    op.create_table("order_fulfillments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("operator_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("code_item_id", sa.Integer(), sa.ForeignKey("code_items.id"), nullable=False), sa.Column("revealed_code_hash", sa.String(128), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))

    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True), sa.Column("action", sa.String(128), nullable=False), sa.Column("entity_type", sa.String(64), nullable=False), sa.Column("entity_id", sa.String(64), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_audit_logs_entity_created", "audit_logs", ["entity_type", "entity_id", sa.text("created_at DESC")], unique=False)


def downgrade() -> None:
    for table in ["audit_logs", "order_fulfillments", "price_snapshots", "code_items", "orders", "fx_rates", "promotion_cost_rules", "pricing_configs", "sell_nominals", "purchase_batches", "supplier_code_types", "users"]:
        op.drop_table(table)
