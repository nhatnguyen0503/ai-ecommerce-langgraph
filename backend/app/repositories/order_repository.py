from sqlalchemy import select
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models import Order


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, order_id: str) -> Order | None:
        """Get order by id"""
        stmt = select(Order).where(Order.id == order_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> Sequence[Order]:
        """List all orders"""
        stmt = select(Order)
        return self.session.execute(stmt).scalars().all()
