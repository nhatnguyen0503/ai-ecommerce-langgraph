import pytest


# --- admin: full access ---

def test_admin_can_list_orders(client, admin_headers):
    response = client.get("/orders", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_order_accepts_lowercase_id(client, admin_headers):
    response = client.get("/orders/fi-10234", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "FI-10234"


def test_get_order_missing_returns_404(client, admin_headers):
    response = client.get("/orders/xxx", headers=admin_headers)
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Order XXX not found"
    assert body["request_id"]


def test_return_eligibility_shape(client, owner_headers):
    response = client.get("/orders/FI-10234/return-eligibility", headers=owner_headers)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"eligible", "days_since_delivery", "reason"}
    assert isinstance(body["eligible"], bool)


def test_return_eligibility_missing_order_is_404(client, admin_headers):
    response = client.get("/orders/nope/return-eligibility", headers=admin_headers)
    assert response.status_code == 404


# --- authorization matrix ---

@pytest.mark.parametrize("path", ["/orders", "/orders/FI-10234", "/orders/FI-10234/return-eligibility"])
def test_all_order_endpoints_require_login(client, path):
    assert client.get(path).status_code == 401


def test_customer_cannot_list_all_orders(client, owner_headers):
    assert client.get("/orders", headers=owner_headers).status_code == 403


def test_owner_can_see_own_order(client, owner_headers):
    assert client.get("/orders/FI-10234", headers=owner_headers).status_code == 200


@pytest.mark.parametrize("path", ["/orders/FI-10234", "/orders/FI-10234/return-eligibility"])
def test_other_customer_gets_404_same_as_missing(client, other_headers, path):
    response = client.get(path, headers=other_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order FI-10234 not found"
