def login(client, email: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_viewer_forbidden_to_recalculate(client):
    token = login(client, "viewer@test.com", "viewer123")
    r = client.post("/api/v1/pricing/recalculate", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_can_patch_settings(client):
    token = login(client, "admin@test.com", "admin123")
    r = client.patch("/api/v1/settings", json={"marketplace_fee_percent": 11}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["marketplace_fee_percent"] == 11
