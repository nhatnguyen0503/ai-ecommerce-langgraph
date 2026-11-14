import logging
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import SessionLocal
from app.errors import error_response, register_exception_handlers
from app.logging_config import setup_logging
from app.request_context import request_id_var, resolve_request_id
from app.routers import auth, orders
from app.seed import seed

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting app (env=%s)", settings.app_env)
    with SessionLocal() as db:
        seed(db)
    yield
    logger.info("Shutting down")


class DocsUrls(TypedDict):
    docs_url: str | None
    redoc_url: str | None
    openapi_url: str | None


def api_docs_urls(app_env: str) -> DocsUrls:
    """Swagger/ReDoc/OpenAPI are for development only."""
    if app_env == "prod":
        return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    return {"docs_url": "/docs", "redoc_url": "/redoc", "openapi_url": "/openapi.json"}


app = FastAPI(
    title="Smart E-commerce support agent",
    lifespan=lifespan,
    **api_docs_urls(get_settings().app_env),
)
app.include_router(orders.router)
app.include_router(auth.router)
register_exception_handlers(app)

# Sent on every response; cheap browser-side protections for an API.
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    token = request_id_var.set(request_id)
    try:
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled error on %s %s", request.method, request.url.path)
            response = error_response(500, "Internal server error")
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = request_id
    for name, value in SECURITY_HEADERS.items():
        response.headers[name] = value
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
