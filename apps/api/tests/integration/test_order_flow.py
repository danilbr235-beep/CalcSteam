from datetime import datetime, timedelta

from app.models.enums import CodeStatus
from app.models.models import CodeItem, FxRate, SellNominal
from app.services.pricing_service import PricingService


def login(client, email: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_stale_rate_warning(db_session):
    db_session.query(FxRate).delete()
    db_session.add(
        FxRate(
            from_currency="SGD",
            to_currency="EUR",
            rate=0.68,
            source="old",
            fetched_at=datetime.utcnow() - timedelta(hours=5),
        )
    )
    db_session.commit()
    nominal = db_session.query(SellNominal).first()
    rec = PricingService(db_session).get_best_recommendation(
        nominal, 1000, stale_after_minutes=60
    )
    assert rec["status"] == "stale_rate"


def test_recalculate_snapshots(db_session):
    count = PricingService(db_session).recalculate_all(default_revenue_rub=1200)
    assert count >= 1


def test_create_order_reserve_fulfill_flow(client, db_session):
    token = login(client, "operator@test.com", "operator123")
    nominal_id = db_session.query(SellNominal).first().id
    code_id = db_session.query(CodeItem).first().id

    create = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "external_ref": "ORD-001",
            "sell_nominal_id": nominal_id,
            "expected_revenue_rub": 1200,
        },
    )
    assert create.status_code == 200
    order_id = create.json()["id"]

    reserve = client.post(
        f"/api/v1/orders/{order_id}/reserve",
        headers={"Authorization": f"Bearer {token}", "X-Idempotency-Key": "reserve-1"},
        json={"code_ids": [code_id], "ttl_minutes": 15},
    )
    assert reserve.status_code == 200

    fulfill = client.post(
        f"/api/v1/orders/{order_id}/fulfill",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fulfill.status_code == 200
    assert len(fulfill.json()["codes"]) == 1

    code = db_session.query(CodeItem).filter(CodeItem.id == code_id).first()
    assert code.status == CodeStatus.sent


def test_blocked_double_reserve(client, db_session):
    token = login(client, "operator@test.com", "operator123")
    nominal_id = db_session.query(SellNominal).first().id
    code_id = db_session.query(CodeItem).first().id

    create1 = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "external_ref": "ORD-100",
            "sell_nominal_id": nominal_id,
            "expected_revenue_rub": 1200,
        },
    )
    create2 = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "external_ref": "ORD-101",
            "sell_nominal_id": nominal_id,
            "expected_revenue_rub": 1200,
        },
    )
    o1, o2 = create1.json()["id"], create2.json()["id"]

    r1 = client.post(
        f"/api/v1/orders/{o1}/reserve",
        headers={"Authorization": f"Bearer {token}", "X-Idempotency-Key": "r1"},
        json={"code_ids": [code_id]},
    )
    assert r1.status_code == 200

    r2 = client.post(
        f"/api/v1/orders/{o2}/reserve",
        headers={"Authorization": f"Bearer {token}", "X-Idempotency-Key": "r2"},
        json={"code_ids": [code_id]},
    )
    assert r2.status_code == 409


def test_viewer_cannot_reveal_or_fulfill(client, db_session):
    operator = login(client, "operator@test.com", "operator123")
    viewer = login(client, "viewer@test.com", "viewer123")
    nominal_id = db_session.query(SellNominal).first().id
    code_id = db_session.query(CodeItem).first().id

    create = client.post(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {operator}"},
        json={"external_ref": "ORD-777", "sell_nominal_id": nominal_id, "expected_revenue_rub": 1100},
    )
    order_id = create.json()["id"]
    client.post(
        f"/api/v1/orders/{order_id}/reserve",
        headers={"Authorization": f"Bearer {operator}", "X-Idempotency-Key": "r777"},
        json={"code_ids": [code_id]},
    )

    reveal = client.get(
        f"/api/v1/inventory/codes/{code_id}/reveal",
        headers={"Authorization": f"Bearer {viewer}"},
    )
    assert reveal.status_code == 403

    fulfill = client.post(
        f"/api/v1/orders/{order_id}/fulfill",
        headers={"Authorization": f"Bearer {viewer}"},
    )
    assert fulfill.status_code == 403
