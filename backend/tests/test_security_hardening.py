import pytest

from app.main import SECURITY_HEADERS, api_docs_urls

ORIGIN = "http://localhost:5173"


# --- 14.3 security headers ---


@pytest.mark.parametrize("path", ["/health", "/orders/FI-10234", "/does-not-exist"])
def test_security_headers_on_every_response(client, path):
    # 200, 401 and 404 responses must all carry the headers
    response = client.get(path)
    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


# --- 14.4 docs only outside prod ---


def test_docs_disabled_in_prod():
    assert api_docs_urls("prod") == {"docs_url": None, "redoc_url": None, "openapi_url": None}


@pytest.mark.parametrize("env", ["dev", "test"])
def test_docs_enabled_outside_prod(env):
    assert api_docs_urls(env)["docs_url"] == "/docs"


# --- 14.4 tighter CORS ---


def test_cors_allows_authorization_header(client):
    response = client.options(
        "/orders",
        headers={
            "Origin": ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200


def test_cors_rejects_unused_method(client):
    response = client.options(
        "/orders",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "DELETE"},
    )
    assert response.status_code == 400
