import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.config import get_settings
from app.database import SessionLocal
from app.errors import error_response, register_exception_handlers
from app.logging_config import setup_logging
from app.request_context import request_id_var, resolve_request_id
from app.routers import orders
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


app = FastAPI(title="Smart E-commerce support agent", lifespan=lifespan)
app.include_router(orders.router)
register_exception_handlers(app)


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
    return response


@app.get("/health")
def health():
    return {"status": "ok"}
