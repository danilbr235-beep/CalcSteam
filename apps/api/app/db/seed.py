from datetime import datetime
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import CodeStatus, UserRole
from app.models.models import CodeItem, FxRate, PricingConfig, PurchaseBatch, SellNominal, SupplierCodeType, User
from app.utils.crypto import encrypt_code, mask_code


def usd_eur_nominals() -> list[int]:
    return [1, 2, 5, *list(range(10, 105, 5)), 200, 300, 400, 500, 1000]


def run() -> None:
    db = SessionLocal()
    users = [
        User(email="admin@local", password_hash=hash_password("admin123"), role=UserRole.admin),
        User(email="operator@local", password_hash=hash_password("operator123"), role=UserRole.operator),
        User(email="viewer@local", password_hash=hash_password("viewer123"), role=UserRole.viewer),
    ]
    db.add_all(users)

    sgd = [10, 20, 30, 40, 50, 100]
    myr = [5, 8, 10, 13, 15, 20]
    code_types = [* [SupplierCodeType(currency="SGD", face_value=v) for v in sgd], * [SupplierCodeType(currency="MYR", face_value=v) for v in myr]]
    db.add_all(code_types)

    for cur in ["USD", "EUR"]:
        for n in usd_eur_nominals():
            db.add(SellNominal(currency=cur, nominal=n))
    for n in [500, 1000, 2500, 5000, 10000, 15000, 25000, 50000, 75000, 100000]:
        db.add(SellNominal(currency="KZT", nominal=n))
    for n in [6, 15, 36, 100, 200, 350, 700, 1000]:
        db.add(SellNominal(currency="CNY", nominal=n))

    db.add(PricingConfig(marketplace_fee_percent=10, risk_reserve_percent=3, min_profit_rub=30, target_profit_percent=7, rounding_rule="ceil_10", max_codes_per_order=3, underfill_tolerance_percent=3, overfill_tolerance_percent=3, ad_allocation_mode="flat", default_ad_cost_per_sale=20, is_active=True))

    batch = PurchaseBatch(supplier_name="Demo Supplier", purchased_at=datetime.utcnow(), note="demo")
    db.add(batch)
    db.flush()
    for i, typ in enumerate(code_types[:6]):
        raw = f"DEMO-CODE-{i}-ABCDEFG"
        db.add(CodeItem(batch_id=batch.id, supplier_code_type_id=typ.id, encrypted_code=encrypt_code(raw), masked_code=mask_code(raw), purchase_cost_rub=300 + i * 10, status=CodeStatus.new))

    fx_demo = [
        ("SGD", "USD", 0.74), ("SGD", "EUR", 0.68), ("SGD", "KZT", 350), ("SGD", "CNY", 5.3),
        ("MYR", "USD", 0.21), ("MYR", "EUR", 0.19), ("MYR", "KZT", 100), ("MYR", "CNY", 1.5),
    ]
    for a, b, r in fx_demo:
        db.add(FxRate(from_currency=a, to_currency=b, rate=r, source="seed", fetched_at=datetime.utcnow()))

    db.commit()
    db.close()


if __name__ == "__main__":
    run()
