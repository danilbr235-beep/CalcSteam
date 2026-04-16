from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import PromotionCostRule, User
from app.schemas.settings import PricingConfigPatch, PricingConfigRead, PromotionRuleCreate
from app.services.audit_service import log_action
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=PricingConfigRead)
def get_settings(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return SettingsService(db).get_active_config()


@router.patch("", response_model=PricingConfigRead)
def patch_settings(
    payload: PricingConfigPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_role(UserRole.admin)),
):
    row = SettingsService(db).patch_active_config(payload.model_dump())
    log_action(db, user.id, "settings.update", "pricing_config", str(row.id), payload.model_dump())
    return row


@router.get("/promotion-rules")
def get_rules(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(PromotionCostRule).order_by(PromotionCostRule.id.desc()).all()


@router.post("/promotion-rules")
def create_rule(
    payload: PromotionRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_role(UserRole.admin)),
):
    row = SettingsService(db).create_promotion_rule(
        payload.currency,
        payload.nominal_from,
        payload.nominal_to,
        payload.ad_cost_rub,
    )
    log_action(db, user.id, "promotion_rule.create", "promotion_cost_rule", str(row.id), payload.model_dump())
    return row
