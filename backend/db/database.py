"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# Use DATABASE_URL from environment variable if available, otherwise fallback to local SQLite
# Note: Render provides postgres:// URLs, but SQLAlchemy requires postgresql://
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./interview.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) if "sqlite" in DATABASE_URL else create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
