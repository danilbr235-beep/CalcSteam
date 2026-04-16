from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import combinations
from math import inf
from sqlalchemy.orm import Session
from app.models.enums import CodeStatus, ItemRiskStatus
from app.models.models import (
    CodeItem,
    FxRate,
    PriceSnapshot,
    PricingConfig,
    PromotionCostRule,
    SellNominal,
    SupplierCodeType,
)


@dataclass
class ComboEval:
    code_ids: list[int]
    delivered_value: float
    combo_cost_rub: float
    reserve_rub: float
    target_profit_rub: float
    recommended_price_rub: float
    expected_net_profit: float
    deviation_percent: float
    valid: bool


class PricingService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _apply_rounding(value: float, rule: str) -> float:
        if rule == "ceil_10":
            return (int(value + 9) // 10) * 10
        if rule == "ceil_1":
            return float(int(value + 0.9999))
        if rule == "bankers_2":
            return round(value, 2)
        return round(value, 2)

    def _ad_cost_for_nominal(self, currency: str, nominal: float, cfg: PricingConfig) -> float:
        rule = (
            self.db.query(PromotionCostRule)
            .filter(
                PromotionCostRule.currency == currency,
                PromotionCostRule.nominal_from <= nominal,
                PromotionCostRule.nominal_to >= nominal,
            )
            .order_by(PromotionCostRule.id.desc())
            .first()
        )
        return rule.ad_cost_rub if rule else cfg.default_ad_cost_per_sale

    def evaluate_combo(
        self,
        delivered_value: float,
        combo_cost_rub: float,
        revenue_rub: float,
        cfg: PricingConfig,
        ad_cost_per_sale: float,
        target_nominal: float,
    ) -> ComboEval:
        reserve_rub = combo_cost_rub * cfg.risk_reserve_percent / 100
        target_profit_rub = max(combo_cost_rub * cfg.target_profit_percent / 100, cfg.min_profit_rub)
        base_required_rub = combo_cost_rub + ad_cost_per_sale + reserve_rub + target_profit_rub
        recommended_price_rub = base_required_rub / (1 - cfg.marketplace_fee_percent / 100)
        recommended_price_rub = self._apply_rounding(recommended_price_rub, cfg.rounding_rule)
        marketplace_fee_rub = revenue_rub * cfg.marketplace_fee_percent / 100
        expected_net_profit = revenue_rub - marketplace_fee_rub - combo_cost_rub - ad_cost_per_sale - reserve_rub
        deviation_percent = abs(delivered_value - target_nominal) / target_nominal * 100
        valid = (
            delivered_value >= target_nominal * (1 - cfg.underfill_tolerance_percent / 100)
            and delivered_value <= target_nominal * (1 + cfg.overfill_tolerance_percent / 100)
        )
        return ComboEval(
            [],
            delivered_value,
            combo_cost_rub,
            reserve_rub,
            target_profit_rub,
            recommended_price_rub,
            expected_net_profit,
            deviation_percent,
            valid,
        )

    def _latest_rate_map(self) -> dict[tuple[str, str], FxRate]:
        rows = self.db.query(FxRate).order_by(FxRate.fetched_at.desc()).all()
        out: dict[tuple[str, str], FxRate] = {}
        for row in rows:
            out.setdefault((row.from_currency, row.to_currency), row)
        return out

    def get_best_recommendation(
        self,
        sell_nominal: SellNominal,
        revenue_rub: float,
        stale_after_minutes: int = 120,
    ) -> dict:
        cfg = (
            self.db.query(PricingConfig)
            .filter(PricingConfig.is_active.is_(True))
            .order_by(PricingConfig.id.desc())
            .first()
        )
        if not cfg:
            raise ValueError("No active pricing config")

        available_codes = (
            self.db.query(CodeItem, SupplierCodeType)
            .join(SupplierCodeType, SupplierCodeType.id == CodeItem.supplier_code_type_id)
            .filter(CodeItem.status == CodeStatus.new)
            .all()
        )
        rate_map = self._latest_rate_map()

        scored: list[ComboEval] = []
        stale_rate = False
        for r in range(1, cfg.max_codes_per_order + 1):
            for combo in combinations(available_codes, r):
                code_ids = [c.id for c, _ in combo]
                combo_cost = sum(c.purchase_cost_rub for c, _ in combo)
                delivered = 0.0
                for _, typ in combo:
                    fx_key = (typ.currency, sell_nominal.currency)
                    fx = rate_map.get(fx_key)
                    if not fx:
                        delivered = -1
                        break
                    if fx.fetched_at < datetime.utcnow() - timedelta(minutes=stale_after_minutes):
                        stale_rate = True
                    delivered += typ.face_value * fx.rate
                if delivered < 0:
                    continue
                ad_cost = self._ad_cost_for_nominal(sell_nominal.currency, sell_nominal.nominal, cfg)
                e = self.evaluate_combo(
                    delivered,
                    combo_cost,
                    revenue_rub,
                    cfg,
                    ad_cost,
                    sell_nominal.nominal,
                )
                e.code_ids = code_ids
                scored.append(e)

        if not scored:
            return {"status": ItemRiskStatus.no_combo.value, "manual_review": True}

        valid = [x for x in scored if x.valid]
        candidates = valid or scored
        best = sorted(
            candidates,
            key=lambda x: (-x.expected_net_profit, len(x.code_ids), x.deviation_percent),
        )[0]
        status = ItemRiskStatus.ok.value if valid else ItemRiskStatus.manual_review.value
        if stale_rate:
            status = ItemRiskStatus.stale_rate.value
        if best.expected_net_profit < 0:
            status = ItemRiskStatus.loss.value
        return {
            "status": status,
            "manual_review": not bool(valid),
            "best_combo": best.code_ids,
            "delivered_value": best.delivered_value,
            "recommended_price_rub": best.recommended_price_rub,
            "expected_profit_rub": best.expected_net_profit,
            "margin_percent": (best.expected_net_profit / revenue_rub * 100) if revenue_rub else -inf,
        }

    def recalculate_all(self, default_revenue_rub: float = 1000) -> int:
        count = 0
        for nominal in self.db.query(SellNominal).filter(SellNominal.is_active.is_(True)).all():
            rec = self.get_best_recommendation(nominal, default_revenue_rub)
            self.db.add(
                PriceSnapshot(
                    sell_nominal_id=nominal.id,
                    recommended_price_rub=rec.get("recommended_price_rub", 0),
                    best_combo={"code_ids": rec.get("best_combo", [])},
                    estimated_profit_rub=rec.get("expected_profit_rub", 0),
                    margin_percent=rec.get("margin_percent", 0),
                    status=rec["status"],
                )
            )
            count += 1
        self.db.commit()
        return count
