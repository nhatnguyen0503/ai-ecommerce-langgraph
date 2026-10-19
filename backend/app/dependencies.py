from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


def get_order_repository(db: Annotated[Session, Depends(get_db)]) -> OrderRepository:
    """Dependency to provide an instance of OrderRepository."""
    return OrderRepository(db)

def get_order_service(repo: Annotated[OrderRepository, Depends(get_order_repository)]) -> OrderService:
    """Dependency to provide an instance of OrderService."""
    return OrderService(repo, window_days=get_settings().return_window_days)
