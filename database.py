# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite DB stored in this file
DATABASE_URL = "sqlite:///./expense_tracker.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite with threads
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Import models and create tables.
    Call this once at startup.
    """
    import models  # noqa: F401  (import only to register models with Base)
    Base.metadata.create_all(bind=engine)
