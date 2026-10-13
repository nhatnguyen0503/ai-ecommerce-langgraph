"""Mocked email service.

Nothing actually goes over SMTP for this demo: every "send" is logged to the
console and persisted to the `sent_emails` table so the admin dashboard (and
tests) can inspect exactly what would have been sent to the customer.
"""
from app_reference.database import SessionLocal
from app_reference.models import SentEmail


def send_email(to_email: str, subject: str, body: str, order_id: str | None = None) -> SentEmail:
    print(f"\n----- [MOCK EMAIL] -----\nTo: {to_email}\nSubject: {subject}\n\n{body}\n------------------------\n")
    db = SessionLocal()
    try:
        record = SentEmail(to_email=to_email, subject=subject, body=body, order_id=order_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()
