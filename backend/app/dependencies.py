from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import get_settings
from app.database import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.models import User
from app.security import InvalidTokenError, decode_access_token


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


# Reads "Authorization: Bearer <token>"; if the header is missing it returns 401
# by itself. tokenUrl tells Swagger's "Authorize" button where to log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError):
        raise _credentials_error() from None
    user = repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise _credentials_error()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
