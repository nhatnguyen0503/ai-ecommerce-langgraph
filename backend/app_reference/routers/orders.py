"""Mock order-lookup API.

Stands in for the endpoints that would normally live on the existing Laravel
backend (order status, shipping, etc). The LangGraph agent talks to this same
data through `app_reference.agent.business.find_order` rather than over HTTP, but it's
exposed here too so the frontend (or curl) can browse the seeded orders.
"""
from fastapi import APIRouter, HTTPException

from app_reference.agent.business import find_order
from app_reference.database import SessionLocal
from app_reference.models import Order
from app_reference.schemas import OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders():
    db = SessionLocal()
    try:
        return db.query(Order).all()
    finally:
        db.close()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str):
    order = find_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order
