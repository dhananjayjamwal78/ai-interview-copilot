from app.main import create_app


def test_root_endpoint_returns_service_metadata(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "AI Interview Copilot backend is running"
    assert body["docs"] == "/docs"
    assert body["health"] == "/health"


def test_health_endpoint_returns_ok_when_database_is_available(client, monkeypatch):
    monkeypatch.setattr("app.services.health_service.check_database_connection", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"


def test_auth_signup_login_and_me_flow(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "tester@example.com",
            "full_name": "Tester Example",
            "password": "strongpass123",
        },
    )
    assert signup_response.status_code == 201
    token = signup_response.json()["access_token"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": "TESTER@example.com",
            "password": "strongpass123",
        },
    )
    assert login_response.status_code == 200

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "tester@example.com"


def test_protected_route_requires_authentication(client):
    response = client.get("/sessions")

    assert response.status_code == 401


def test_create_app_smoke():
    test_app = create_app()

    paths = {route.path for route in test_app.routes}
    assert "/" in paths
    assert "/health" in paths
    assert "/auth/signup" in paths
