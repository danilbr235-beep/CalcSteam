from datetime import datetime
from pydantic import BaseModel


class PricingSimulationRequest(BaseModel):
    sell_nominal_id: int
    custom_revenue_rub: float


class RecalculateResponse(BaseModel):
    snapshots_created: int


class SnapshotRead(BaseModel):
    id: int
    sell_nominal_id: int
    recommended_price_rub: float
    best_combo: dict
    estimated_profit_rub: float
    margin_percent: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
