import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import orders
from app.seed import seed
from app.services.order_service import OrderNotFoundError
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting app (env=%s)", settings.app_env)
    seed()
    yield
    logger.info("Shutting down")


app = FastAPI(title="Smart E-commerce support agent", lifespan=lifespan)
app.include_router(orders.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
