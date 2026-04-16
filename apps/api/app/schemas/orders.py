from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    external_ref: str
    sell_nominal_id: int
    expected_revenue_rub: float = Field(gt=0)


class ReserveOrderRequest(BaseModel):
    code_ids: list[int]
    ttl_minutes: int | None = Field(default=None, ge=1, le=120)


class FulfillResponse(BaseModel):
    order_id: int
    codes: list[str]
    status: str
