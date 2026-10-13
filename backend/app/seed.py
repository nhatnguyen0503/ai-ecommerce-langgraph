from datetime import datetime, timedelta

from app.database import SessionLocal, init_db
from app.models import Order


def days_ago(n: int) -> datetime:
    return datetime.utcnow() - timedelta(days=n)


SAMPLE_ORDERS = [
    # giao 3 ngày trước, 29.90€ -> trả hàng sẽ tự duyệt
    dict(id="FI-10234", customer_name="Aino Korhonen", customer_email="aino@example.fi",
         items=[{"name": "Wool Beanie", "qty": 1, "price": 29.90}],
         total_amount=29.90, status="delivered", warehouse="Posti Helsinki Hub",
         order_date=days_ago(5), delivered_date=days_ago(3)),
    # giao 18 ngày trước -> quá hạn 14 ngày
    dict(id="FI-10235", customer_name="Mikko Virtanen", customer_email="mikko@example.fi",
         items=[{"name": "Mechanical Keyboard", "qty": 1, "price": 149.00},
                {"name": "USB-C Cable", "qty": 2, "price": 9.90}],
         total_amount=168.80, status="delivered", warehouse="Posti Tampere Hub",
         order_date=days_ago(20), delivered_date=days_ago(18)),
    # giao 7 ngày trước, 219€ -> vượt 100€, cần admin duyệt
    dict(id="FI-10236", customer_name="Liisa Nieminen", customer_email="liisa@example.fi",
         items=[{"name": "Winter Jacket", "qty": 1, "price": 219.00}],
         total_amount=219.00, status="delivered", warehouse="Posti Turku Hub",
         order_date=days_ago(9), delivered_date=days_ago(7)),
    # đang vận chuyển, chưa giao
    dict(id="FI-10237", customer_name="Juha Makela", customer_email="juha@example.fi",
         items=[{"name": "Bluetooth Speaker", "qty": 1, "price": 79.90}],
         total_amount=79.90, status="in_transit", warehouse="Posti Helsinki Hub",
         order_date=days_ago(1), delivered_date=None),
    # giao 42 ngày trước -> quá hạn
    dict(id="FI-10238", customer_name="Emilia Lahtinen", customer_email="emilia@example.fi",
         items=[{"name": "Coffee Maker", "qty": 1, "price": 89.00}],
         total_amount=89.00, status="delivered", warehouse="Posti Oulu Hub",
         order_date=days_ago(45), delivered_date=days_ago(42)),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Order).count() > 0:
            return
        for data in SAMPLE_ORDERS:
            db.add(Order(**data))
        db.commit()
    finally:
        db.close()