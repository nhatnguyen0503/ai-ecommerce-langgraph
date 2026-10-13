"""Seed the mock Finnish e-commerce database with sample orders.

Run with:  python -m app_reference.seed
"""
from datetime import datetime, timedelta

from app_reference.database import SessionLocal, init_db
from app_reference.models import Order

NOW = datetime.utcnow()

SAMPLE_ORDERS = [
    dict(
        id="FI-10234",
        customer_name="Aino Korhonen",
        customer_email="aino.korhonen@example.fi",
        items=[{"name": "Wool Beanie", "qty": 1, "price": 29.90}],
        total_amount=29.90,
        status="delivered",
        warehouse="Posti Helsinki Hub",
        order_date=NOW - timedelta(days=5),
        delivered_date=NOW - timedelta(days=3),
    ),
    dict(
        id="FI-10235",
        customer_name="Mikko Virtanen",
        customer_email="mikko.virtanen@example.fi",
        items=[
            {"name": "Mechanical Keyboard", "qty": 1, "price": 149.00},
            {"name": "USB-C Cable", "qty": 2, "price": 9.90},
        ],
        total_amount=168.80,
        status="delivered",
        warehouse="Posti Tampere Hub",
        order_date=NOW - timedelta(days=20),
        delivered_date=NOW - timedelta(days=18),
    ),
    dict(
        id="FI-10236",
        customer_name="Liisa Nieminen",
        customer_email="liisa.nieminen@example.fi",
        items=[{"name": "Winter Jacket", "qty": 1, "price": 219.00}],
        total_amount=219.00,
        status="delivered",
        warehouse="Posti Turku Hub",
        order_date=NOW - timedelta(days=9),
        delivered_date=NOW - timedelta(days=7),
    ),
    dict(
        id="FI-10237",
        customer_name="Juha Makela",
        customer_email="juha.makela@example.fi",
        items=[{"name": "Bluetooth Speaker", "qty": 1, "price": 79.90}],
        total_amount=79.90,
        status="in_transit",
        warehouse="Posti Helsinki Hub",
        order_date=NOW - timedelta(days=1),
        delivered_date=None,
    ),
    dict(
        id="FI-10238",
        customer_name="Emilia Lahtinen",
        customer_email="emilia.lahtinen@example.fi",
        items=[{"name": "Coffee Maker", "qty": 1, "price": 89.00}],
        total_amount=89.00,
        status="delivered",
        warehouse="Posti Oulu Hub",
        order_date=NOW - timedelta(days=45),
        delivered_date=NOW - timedelta(days=42),
    ),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Order).count() > 0:
            print("Orders already seeded, skipping.")
            return
        for data in SAMPLE_ORDERS:
            db.add(Order(**data))
        db.commit()
        print(f"Seeded {len(SAMPLE_ORDERS)} mock orders.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
