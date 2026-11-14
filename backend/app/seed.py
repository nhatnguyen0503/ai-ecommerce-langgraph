import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import utc_now_naive
from app.config import get_settings
from app.models import Order, User
from app.security import hash_password

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "admin@example.com"


def days_ago(n: int) -> datetime:
    return utc_now_naive() - timedelta(days=n)


SAMPLE_ORDERS = [
    # delivered 3 days ago, 29.90€ -> return auto-approved
    dict(
        id="FI-10234",
        customer_name="Aino Korhonen",
        customer_email="aino@example.fi",
        items=[{"name": "Wool Beanie", "qty": 1, "price": 29.90}],
        total_amount=29.90,
        status="delivered",
        warehouse="Posti Helsinki Hub",
        order_date=days_ago(5),
        delivered_date=days_ago(3),
    ),
    # delivered 18 days ago, 168.80€ -> return auto-rejected (past 14-day window)
    dict(
        id="FI-10235",
        customer_name="Mikko Virtanen",
        customer_email="mikko@example.fi",
        items=[
            {"name": "Mechanical Keyboard", "qty": 1, "price": 149.00},
            {"name": "USB-C Cable", "qty": 2, "price": 9.90},
        ],
        total_amount=168.80,
        status="delivered",
        warehouse="Posti Tampere Hub",
        order_date=days_ago(20),
        delivered_date=days_ago(18),
    ),
    # delivered 7 days ago, 219€ -> exceeds 100€, requires admin approval
    dict(
        id="FI-10236",
        customer_name="Liisa Nieminen",
        customer_email="liisa@example.fi",
        items=[{"name": "Winter Jacket", "qty": 1, "price": 219.00}],
        total_amount=219.00,
        status="delivered",
        warehouse="Posti Turku Hub",
        order_date=days_ago(9),
        delivered_date=days_ago(7),
    ),
    # in transit, not delivered
    dict(
        id="FI-10237",
        customer_name="Juha Makela",
        customer_email="juha@example.fi",
        items=[{"name": "Bluetooth Speaker", "qty": 1, "price": 79.90}],
        total_amount=79.90,
        status="in_transit",
        warehouse="Posti Helsinki Hub",
        order_date=days_ago(1),
        delivered_date=None,
    ),
    # delivered 42 days ago -> past the return window
    dict(
        id="FI-10238",
        customer_name="Emilia Lahtinen",
        customer_email="emilia@example.fi",
        items=[{"name": "Coffee Maker", "qty": 1, "price": 89.00}],
        total_amount=89.00,
        status="delivered",
        warehouse="Posti Oulu Hub",
        order_date=days_ago(45),
        delivered_date=days_ago(42),
    ),
]


def seed_users(db: Session, password: str, app_env: str) -> int:
    """Create one admin + one customer per sample order email. Returns how many were created."""
    if app_env == "prod" or not password:
        logger.info("Skipping demo users (env=%s)", app_env)
        return 0

    wanted = {ADMIN_EMAIL: "admin"}
    wanted.update({o["customer_email"]: "customer" for o in SAMPLE_ORDERS})

    existing = set(db.scalars(select(User.email)))
    created = 0
    for email, role in wanted.items():
        if email in existing:
            continue
        db.add(User(email=email, hashed_password=hash_password(password), role=role))
        created += 1
    db.commit()
    logger.info("Seeded %d demo users", created)  # count only — no emails in logs
    return created


def seed(db: Session) -> None:
    settings = get_settings()
    seed_users(db, settings.seed_demo_password.get_secret_value(), settings.app_env)
    if db.query(Order).count() > 0:
        return
    user_ids = {u.email: u.id for u in db.scalars(select(User))}
    for data in SAMPLE_ORDERS:
        db.add(Order(**data, user_id=user_ids.get(data["customer_email"])))
    db.commit()
