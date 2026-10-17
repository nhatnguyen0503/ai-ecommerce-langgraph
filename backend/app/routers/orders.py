from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
