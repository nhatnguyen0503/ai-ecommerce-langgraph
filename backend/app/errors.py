from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.request_context import request_id_var
from app.services.order_service import OrderNotFoundError
from app.services.auth_service import InvalidCredentialsError


def error_response(status_code: int, detail, headers: dict[str, str] | None = None) -> JSONResponse:
    """Build the one error shape used by the whole API."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "request_id": request_id_var.get()},
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(OrderNotFoundError)
    async def order_not_found(request: Request, exc: OrderNotFoundError):
        return error_response(404, str(exc))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return error_response(422, exc.errors())

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials(request: Request, exc: InvalidCredentialsError):
        return error_response(401, str(exc), headers={"WWW-Authenticate": "Bearer"})

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, exc.detail, headers=getattr(exc, "headers", None))
