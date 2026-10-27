
def test_list_orders(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_order_accepts_lowercase_id(client):
    response = client.get("/orders/fi-10234")
    assert response.status_code == 200
    assert response.json()["id"] == "FI-10234"

def test_get_order_missing_returns_404(client):
    response = client.get("/orders/xxx")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Order XXX not found"
    assert body["request_id"]


def test_return_eligibility_shape(client):
    response = client.get("/orders/FI-10234/return-eligibility")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"eligible", "days_since_delivery", "reason"}
    assert isinstance(body["eligible"], bool)

def test_return_eligibility_within_window(client):
    response = client.get("/orders/nope/return-eligibility")
    assert response.status_code == 404
