from sqlalchemy import JSON, Column, DateTime, Float, String

from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    items = Column(JSON, nullable=False)  # [{"name": ..., "qty": ..., "price": ...}]
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    status = Column(String, nullable=False)  # processing | in_transit | delivered
    warehouse = Column(String, default="Posti Helsinki Hub")
    order_date = Column(DateTime, nullable=False)
    delivered_date = Column(DateTime, nullable=True)

