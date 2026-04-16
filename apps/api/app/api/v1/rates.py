from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import FxRate, User
from app.schemas.rates import ManualRateRequest, RateRead
from app.services.audit_service import log_action
from app.services.rates_service import RatesService

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("", response_model=list[RateRead])
def get_rates(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(FxRate).order_by(FxRate.fetched_at.desc()).limit(30).all()


@router.post("/fetch")
def fetch_rates(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_role(UserRole.admin, UserRole.operator)),
):
    created = RatesService(db).fetch_mock_provider()
    log_action(db, user.id, "rates.fetch", "fx_rates", "batch", {"created": created})
    return {"created": created}


@router.post("/manual", response_model=RateRead)
def manual_rate(
    payload: ManualRateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_role(UserRole.admin)),
):
    row = RatesService(db).upsert_manual(
        payload.from_currency,
        payload.to_currency,
        payload.rate,
        payload.source,
    )
    log_action(db, user.id, "rates.manual", "fx_rates", str(row.id), payload.model_dump())
    return row


@router.get("/history", response_model=list[RateRead])
def history(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(FxRate).order_by(FxRate.fetched_at.desc()).limit(300).all()
