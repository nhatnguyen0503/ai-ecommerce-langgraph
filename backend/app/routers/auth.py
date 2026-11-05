from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_auth_service
from app.schemas import TokenOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],
          service: Annotated[AuthService, Depends(get_auth_service)]):
    """Authenticate a user and return an access token."""
    token = service.login(form.username, form.password)
    return TokenOut(access_token=token)
