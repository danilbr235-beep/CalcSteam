from types import SimpleNamespace
from app.services.pricing_service import PricingService


def test_formula_chain_matches_spec():
    svc = PricingService(None)
    cfg = SimpleNamespace(
        risk_reserve_percent=5,
        target_profit_percent=10,
        min_profit_rub=50,
        marketplace_fee_percent=15,
        underfill_tolerance_percent=2,
        overfill_tolerance_percent=2,
        rounding_rule="round_2",
    )
    e = svc.evaluate_combo(
        delivered_value=100,
        combo_cost_rub=500,
        revenue_rub=1000,
        cfg=cfg,
        ad_cost_per_sale=30,
        target_nominal=100,
    )
    assert round(e.reserve_rub, 2) == 25.0
    assert round(e.target_profit_rub, 2) == 50.0
    assert round(e.recommended_price_rub, 2) == round((500 + 30 + 25 + 50) / (1 - 0.15), 2)


def test_rounding_rule():
    assert PricingService._apply_rounding(101.01, "ceil_10") == 110
