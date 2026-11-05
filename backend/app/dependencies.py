from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_order_repository(db: Annotated[Session, Depends(get_db)]) -> OrderRepository:
    """Dependency to provide an instance of OrderRepository."""
    return OrderRepository(db)


def get_order_service(repo: Annotated[OrderRepository, Depends(get_order_repository)]) -> OrderService:
    """Dependency to provide an instance of OrderService."""
    return OrderService(repo, window_days=get_settings().return_window_days)


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Dependency to provide an instance of UserRepository."""
    return UserRepository(db)


def get_auth_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    """Dependency to provide an instance of AuthService."""
    return AuthService(repo)
