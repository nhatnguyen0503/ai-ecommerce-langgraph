"""Pydantic request/response schemas for the API layer."""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel


class OrderItem(BaseModel):
    name: str
    qty: int
    price: float


class OrderOut(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    items: list[OrderItem]
    total_amount: float
    currency: str
    status: str
    warehouse: str
    order_date: datetime
    delivered_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatMessageOut(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    status: Literal["ok", "awaiting_approval"] = "ok"
    messages: list[ChatMessageOut] = []


class PendingApprovalOut(BaseModel):
    id: str
    session_id: str
    order_id: str
    customer_email: str
    refund_amount: float
    reason: str
    status: str
    created_at: datetime
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    admin_note: Optional[str] = None

    model_config = {"from_attributes": True}


class DecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    decided_by: str = "admin"
    note: str = ""


class SentEmailOut(BaseModel):
    id: str
    to_email: str
    subject: str
    body: str
    order_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
