"""SQLAlchemy engine/session setup for the mock e-commerce database."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app_reference.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models so they're registered on Base before create_all
    from app_reference import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
