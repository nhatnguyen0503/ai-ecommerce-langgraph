from datetime import datetime

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
    delivered_date: datetime | None

    model_config = {"from_attributes": True}  # allows Pydantic to read from SQLAlchemy model attributes

class ReturnEligibilityOut(BaseModel):
    eligible: bool
    days_since_delivery: int | None = None
    reason: str


