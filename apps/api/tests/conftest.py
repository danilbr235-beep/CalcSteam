from datetime import datetime
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.enums import CodeStatus, UserRole
from app.models.models import CodeItem, FxRate, PricingConfig, PurchaseBatch, SellNominal, SupplierCodeType, User
from app.utils.crypto import encrypt_code, mask_code
from app.services import reservation_service



@pytest.fixture()
def db_session():
    with tempfile.NamedTemporaryFile(suffix=".db") as fp:
        engine = create_engine(f"sqlite:///{fp.name}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        session = SessionLocal()

        reservation_service.rds = reservation_service.InMemoryLockStore()

        admin = User(email="admin@test.com", password_hash=hash_password("admin123"), role=UserRole.admin)
        operator = User(email="operator@test.com", password_hash=hash_password("operator123"), role=UserRole.operator)
        viewer = User(email="viewer@test.com", password_hash=hash_password("viewer123"), role=UserRole.viewer)
        session.add_all([admin, operator, viewer])
        session.add(PricingConfig(marketplace_fee_percent=10, risk_reserve_percent=3, min_profit_rub=30, target_profit_percent=7, rounding_rule="ceil_10", max_codes_per_order=3, underfill_tolerance_percent=3, overfill_tolerance_percent=3, ad_allocation_mode="flat", default_ad_cost_per_sale=20, is_active=True))
        nom = SellNominal(currency="EUR", nominal=20, is_active=True)
        session.add(nom)
        t = SupplierCodeType(currency="SGD", face_value=20)
        session.add(t)
        session.flush()
        b = PurchaseBatch(supplier_name="t", purchased_at=datetime.utcnow())
        session.add(b)
        session.flush()
        raw = "ABCD-1234-EFGH"
        session.add(CodeItem(batch_id=b.id, supplier_code_type_id=t.id, encrypted_code=encrypt_code(raw), masked_code=mask_code(raw), purchase_cost_rub=500, status=CodeStatus.new))
        session.add(FxRate(from_currency="SGD", to_currency="EUR", rate=0.68, source="seed", fetched_at=datetime.utcnow()))
        session.commit()

        try:
            yield session
        finally:
            session.close()


@pytest.fixture()
def client(db_session):
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]
