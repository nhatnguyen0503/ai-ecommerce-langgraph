from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.request_context import request_id_var
from app.services.order_service import OrderNotFoundError


def error_response(status_code: int, detail) -> JSONResponse:
    """Build the one error shape used by the whole API."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "request_id": request_id_var.get()},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(OrderNotFoundError)
    async def order_not_found(request: Request, exc: OrderNotFoundError):
        return error_response(404, str(exc))

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return error_response(422, exc.errors())
