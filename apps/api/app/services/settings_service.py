from sqlalchemy.orm import Session
from app.models.models import PricingConfig, PromotionCostRule


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_config(self) -> PricingConfig:
        row = (
            self.db.query(PricingConfig)
            .filter(PricingConfig.is_active.is_(True))
            .order_by(PricingConfig.id.desc())
            .first()
        )
        if not row:
            raise ValueError("No active pricing config")
        return row

    def patch_active_config(self, data: dict) -> PricingConfig:
        row = self.get_active_config()
        for key, value in data.items():
            if value is not None:
                setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def create_promotion_rule(self, currency: str, nominal_from: float, nominal_to: float, ad_cost_rub: float) -> PromotionCostRule:
        row = PromotionCostRule(
            currency=currency.upper(),
            nominal_from=nominal_from,
            nominal_to=nominal_to,
            ad_cost_rub=ad_cost_rub,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
