from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from app.config import get_settings
from app.database import init_db
from app.routers import orders
from app.seed import seed
from app.services.order_service import OrderNotFoundError

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    yield

app = FastAPI(title="Smart E-commerce support agent", lifespan=lifespan)
app.include_router(orders.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/config-check")
def config_check():
    return {
        "model": settings.groq_model,
        "return_window_days": settings.return_window_days,
        "ceiling_eur": settings.auto_approve_refund_ceiling_eur,
        "has_api_key": bool(settings.groq_api_key),
    }

@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
