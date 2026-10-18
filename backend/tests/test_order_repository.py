from app.repositories.order_repository import OrderRepository

def test_get_by_id_return_order(db):
    repo = OrderRepository(db)
    order = repo.get_by_id("FI-10234")
    assert order is not None
    assert order.id == "FI-10234"
    assert order.customer_name == "Aino"

def test_list_all_returns_every_order(db):
    repo = OrderRepository(db)
    assert len(repo.list_all()) == 1

def test_get_by_id_returns_none_for_nonexistent_id(db):
    repo = OrderRepository(db)
    order = repo.get_by_id("NOPE")
    assert order is None
