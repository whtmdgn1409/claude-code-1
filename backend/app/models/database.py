"""
Core database engine and session management.
Provides SQLAlchemy engine, session factory, and base class for all models.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session
from sqlalchemy.pool import QueuePool
from app.config import settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.DATABASE_ECHO,
    connect_args={
        "options": "-c timezone=utc"  # Use UTC timezone
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Scoped session for thread-safe access
db_session = scoped_session(SessionLocal)

# Declarative base class for all models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    # Import all models to ensure they're registered with Base
    from app.models import (
        Deal, DealSource, Category, Blacklist,
        User, UserKeyword, UserDevice,
        Bookmark, Notification,
        PriceHistory, DealStatistics, DealKeyword,
        CrawlerRun, CrawlerError, CrawlerState
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables. USE WITH CAUTION!
    Only for development/testing purposes.
    """
    Base.metadata.drop_all(bind=engine)
