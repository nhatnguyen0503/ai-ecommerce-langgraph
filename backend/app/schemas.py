from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class OrderItem(BaseModel):
    name: str
    qtr: int
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

    model_config = {"from_attributes": True}  # cho phép đọc thẳng từ object SQLAlchemy



