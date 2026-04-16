from fastapi import APIRouter, Depends
from app.api.deps import require_role
from app.models.enums import UserRole

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(_=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer))):
    return {"avg_margin": 0, "profit_today": 0, "low_stock": 0}


@router.get("/charts")
def charts(_=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer))):
    return {"profit": [], "orders": []}
