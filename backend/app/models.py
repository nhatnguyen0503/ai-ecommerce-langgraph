from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    customer_name: Mapped[str]
    customer_email: Mapped[str]
    items: Mapped[list[dict]] = mapped_column(JSON)  # [{"name": ..., "qty": ..., "price": ...}]
    total_amount: Mapped[float]
    currency: Mapped[str | None] = mapped_column(default="EUR")
    status: Mapped[str]  # processing | in_transit | delivered
    warehouse: Mapped[str | None] = mapped_column(default="Posti Helsinki Hub")
    order_date: Mapped[datetime]
    delivered_date: Mapped[datetime | None]
