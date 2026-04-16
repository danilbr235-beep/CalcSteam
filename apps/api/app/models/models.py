from datetime import datetime
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import CodeStatus, ItemRiskStatus, OrderStatus, UserRole


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SupplierCodeType(Base, TimestampMixin):
    __tablename__ = "supplier_code_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), index=True)
    face_value: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PurchaseBatch(Base, TimestampMixin):
    __tablename__ = "purchase_batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(255))
    purchased_at: Mapped[datetime] = mapped_column(DateTime)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class CodeItem(Base, TimestampMixin):
    __tablename__ = "code_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("purchase_batches.id"), index=True)
    supplier_code_type_id: Mapped[int] = mapped_column(ForeignKey("supplier_code_types.id"), index=True)
    encrypted_code: Mapped[str] = mapped_column(Text)
    masked_code: Mapped[str] = mapped_column(String(32), index=True)
    purchase_cost_rub: Mapped[float] = mapped_column(Float)
    status: Mapped[CodeStatus] = mapped_column(Enum(CodeStatus), index=True, default=CodeStatus.new)
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reserved_order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)


class SellNominal(Base, TimestampMixin):
    __tablename__ = "sell_nominals"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), index=True)
    nominal: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PricingConfig(Base, TimestampMixin):
    __tablename__ = "pricing_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace_fee_percent: Mapped[float] = mapped_column(Float)
    risk_reserve_percent: Mapped[float] = mapped_column(Float)
    min_profit_rub: Mapped[float] = mapped_column(Float)
    target_profit_percent: Mapped[float] = mapped_column(Float)
    rounding_rule: Mapped[str] = mapped_column(String(64))
    max_codes_per_order: Mapped[int] = mapped_column(Integer)
    underfill_tolerance_percent: Mapped[float] = mapped_column(Float)
    overfill_tolerance_percent: Mapped[float] = mapped_column(Float)
    ad_allocation_mode: Mapped[str] = mapped_column(String(64))
    default_ad_cost_per_sale: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PromotionCostRule(Base, TimestampMixin):
    __tablename__ = "promotion_cost_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), index=True)
    nominal_from: Mapped[float] = mapped_column(Float)
    nominal_to: Mapped[float] = mapped_column(Float)
    ad_cost_rub: Mapped[float] = mapped_column(Float)


class FxRate(Base, TimestampMixin):
    __tablename__ = "fx_rates"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(3))
    to_currency: Mapped[str] = mapped_column(String(3))
    rate: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class PriceSnapshot(Base, TimestampMixin):
    __tablename__ = "price_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    sell_nominal_id: Mapped[int] = mapped_column(ForeignKey("sell_nominals.id"))
    recommended_price_rub: Mapped[float] = mapped_column(Float)
    best_combo: Mapped[dict] = mapped_column(JSON)
    estimated_profit_rub: Mapped[float] = mapped_column(Float)
    margin_percent: Mapped[float] = mapped_column(Float)
    status: Mapped[ItemRiskStatus] = mapped_column(Enum(ItemRiskStatus))


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_ref: Mapped[str] = mapped_column(String(128), unique=True)
    sell_nominal_id: Mapped[int] = mapped_column(ForeignKey("sell_nominals.id"))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), index=True, default=OrderStatus.new)
    expected_revenue_rub: Mapped[float] = mapped_column(Float)
    manual_review: Mapped[bool] = mapped_column(Boolean, default=False)


class OrderFulfillment(Base, TimestampMixin):
    __tablename__ = "order_fulfillments"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    operator_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    code_item_id: Mapped[int] = mapped_column(ForeignKey("code_items.id"))
    revealed_code_hash: Mapped[str] = mapped_column(String(128))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    metadata_json: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index("ix_fx_rates_pair_fetched", FxRate.from_currency, FxRate.to_currency, FxRate.fetched_at.desc())
Index("ix_price_snapshots_nominal_created", PriceSnapshot.sell_nominal_id, PriceSnapshot.created_at.desc())
Index("ix_audit_logs_entity_created", AuditLog.entity_type, AuditLog.entity_id, AuditLog.created_at.desc())
