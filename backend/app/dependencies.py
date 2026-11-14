from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.rate_limit import RateLimiter
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.security import InvalidTokenError, decode_access_token
from app.services.auth_service import AuthService
from app.services.order_service import OrderService


def get_order_repository(db: Annotated[Session, Depends(get_db)]) -> OrderRepository:
    """Dependency to provide an instance of OrderRepository."""
    return OrderRepository(db)


def get_order_service(
    repo: Annotated[OrderRepository, Depends(get_order_repository)],
) -> OrderService:
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user


AdminUser = Annotated[User, Depends(require_admin)]

# 5 login attempts per minute per (client IP, email).
login_limiter = RateLimiter(max_attempts=5, window_seconds=60)


def limit_login_attempts(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{form.username.strip().lower()}"
    retry_after = login_limiter.hit(key)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(int(retry_after) + 1)},
        )
