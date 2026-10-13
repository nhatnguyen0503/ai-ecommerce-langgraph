from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import get_settings
from app.database import init_db
from app.routers import orders
from app.seed import seed

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
        "ceiling_eur": settings.auto_approve_refunds_ceiling_eur,
        "has_api_key": bool(settings.groq_api_key),
    }