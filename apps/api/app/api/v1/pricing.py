from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import PriceSnapshot, SellNominal
from app.schemas.pricing import PricingSimulationRequest, RecalculateResponse, SnapshotRead
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/recommendations")
def recommendations(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    svc = PricingService(db)
    out = []
    for nominal in db.query(SellNominal).filter(SellNominal.is_active.is_(True)).all():
        rec = svc.get_best_recommendation(nominal, 1000)
        out.append(
            {
                "sell_nominal_id": nominal.id,
                "currency": nominal.currency,
                "nominal": nominal.nominal,
                **rec,
            }
        )
    return out


@router.post("/recalculate", response_model=RecalculateResponse)
def recalculate(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin)),
):
    snapshots = PricingService(db).recalculate_all(default_revenue_rub=1000)
    return RecalculateResponse(snapshots_created=snapshots)


@router.get("/snapshots", response_model=list[SnapshotRead])
def get_snapshots(
    sell_nominal_id: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    q = db.query(PriceSnapshot)
    if sell_nominal_id:
        q = q.filter(PriceSnapshot.sell_nominal_id == sell_nominal_id)
    return q.order_by(PriceSnapshot.created_at.desc()).limit(min(limit, 500)).all()


@router.post("/simulate")
def simulate(
    payload: PricingSimulationRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator)),
):
    nominal = db.query(SellNominal).filter(SellNominal.id == payload.sell_nominal_id).first()
    return PricingService(db).get_best_recommendation(nominal, payload.custom_revenue_rub)
