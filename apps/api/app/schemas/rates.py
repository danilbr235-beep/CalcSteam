from datetime import datetime
from pydantic import BaseModel, Field


class ManualRateRequest(BaseModel):
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)
    rate: float = Field(gt=0)
    source: str = "manual"


class RateRead(BaseModel):
    id: int
    from_currency: str
    to_currency: str
    rate: float
    source: str
    fetched_at: datetime

    model_config = {"from_attributes": True}
