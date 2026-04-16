from pydantic import BaseModel, Field


class PricingConfigRead(BaseModel):
    id: int
    marketplace_fee_percent: float
    risk_reserve_percent: float
    min_profit_rub: float
    target_profit_percent: float
    rounding_rule: str
    max_codes_per_order: int
    underfill_tolerance_percent: float
    overfill_tolerance_percent: float
    ad_allocation_mode: str
    default_ad_cost_per_sale: float
    is_active: bool

    model_config = {"from_attributes": True}


class PricingConfigPatch(BaseModel):
    marketplace_fee_percent: float | None = Field(default=None, ge=0, lt=100)
    risk_reserve_percent: float | None = Field(default=None, ge=0)
    min_profit_rub: float | None = Field(default=None, ge=0)
    target_profit_percent: float | None = Field(default=None, ge=0)
    rounding_rule: str | None = None
    max_codes_per_order: int | None = Field(default=None, ge=1, le=6)
    underfill_tolerance_percent: float | None = Field(default=None, ge=0)
    overfill_tolerance_percent: float | None = Field(default=None, ge=0)
    ad_allocation_mode: str | None = None
    default_ad_cost_per_sale: float | None = Field(default=None, ge=0)


class PromotionRuleCreate(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    nominal_from: float
    nominal_to: float
    ad_cost_rub: float = Field(ge=0)
