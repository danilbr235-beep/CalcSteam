from pydantic import BaseModel, Field
from app.models.enums import CodeStatus


class CodeStatusPatch(BaseModel):
    status: CodeStatus


class CodeCreateRequest(BaseModel):
    batch_id: int
    supplier_code_type_id: int
    raw_code: str = Field(min_length=4)
    purchase_cost_rub: float = Field(gt=0)


class CodeRead(BaseModel):
    id: int
    batch_id: int
    supplier_code_type_id: int
    masked_code: str
    status: str
    purchase_cost_rub: float

    model_config = {"from_attributes": True}
