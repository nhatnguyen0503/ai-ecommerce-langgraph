"""SQLAlchemy models for the mock e-commerce store (orders) and the
human-in-the-loop / notification side-tables (pending approvals, sent emails).

In a real deployment `Order` would live in the existing Laravel database and
be reached over HTTP; here it's mocked locally so the whole flow runs
end-to-end without external dependencies.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text, JSON

from app_reference.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)  # human-friendly order code, e.g. "FI-10234"
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    items = Column(JSON, nullable=False)  # [{"name": str, "qty": int, "price": float}]
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    status = Column(String, nullable=False)  # processing | shipped | in_transit | delivered | returned
    warehouse = Column(String, default="Posti Helsinki Hub")
    order_date = Column(DateTime, nullable=False)
    delivered_date = Column(DateTime, nullable=True)


class PendingApproval(Base):
    """A refund/return request awaiting (or having received) admin decision.

    Rows are written just before the LangGraph agent calls `interrupt()`, so
    the admin dashboard can list them via plain SQL without needing to poke
    into the LangGraph checkpointer. Decisions made here are what get fed
    back into the graph as the interrupt's resume value.
    """

    __tablename__ = "pending_approvals"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, nullable=False, index=True)  # LangGraph thread_id
    order_id = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    refund_amount = Column(Float, nullable=False)
    reason = Column(Text, default="")
    status = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String, nullable=True)
    admin_note = Column(Text, nullable=True)


class SentEmail(Base):
    """Mocked outbound email log (approve/reject/auto-approve notifications)."""

    __tablename__ = "sent_emails"

    id = Column(String, primary_key=True, default=_uuid)
    to_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
