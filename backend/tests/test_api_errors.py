from app.dependencies import get_order_service
from app.main import app


def test_response_has_generated_request_id(client):
    response = client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_valid_client_request_id_is_echoed(client):
    response = client.get("/health", headers={"X-Request-ID": "my-test-123"})
    assert response.headers["X-Request-ID"] == "my-test-123"


def test_error_body_contains_request_id(client):
    response = client.get("/orders/xxx", headers={"X-Request-ID": "t-404"})
    assert response.status_code == 404
    assert response.json()["request_id"] == "t-404"


def test_unknown_route_uses_same_error_shape(client):
    response = client.get("/khong-co")
    assert response.status_code == 404
    assert set(response.json()) == {"detail", "request_id"}


def _broken_service():
    raise RuntimeError("secret: postgresql://user:password@db")


def test_unexpected_error_returns_generic_500(client):
    app.dependency_overrides[get_order_service] = _broken_service
    response = client.get("/orders", headers={"X-Request-ID": "t-500"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error", "request_id": "t-500"}
    assert "secret" not in response.text
