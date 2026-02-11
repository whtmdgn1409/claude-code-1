from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.models.database import engine, get_db
from app.models import Base

# Import all models to ensure they're registered
from app.models.deal import DealSource, Category, Deal
from app.models.user import User, UserKeyword, UserDevice
from app.models.interaction import Bookmark, Notification
from app.models.analytics import PriceHistory, DealStatistics, DealKeyword
from app.models.crawler import CrawlerRun, CrawlerError, CrawlerState
from app.models.blacklist import Blacklist


# Create FastAPI application
app = FastAPI(
    title="딜모아 API",
    version="0.1.0",
    description="Korean Hot Deal Aggregation and Notification Service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup event - initialize database."""
    print("🚀 Starting DealMoa API...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")

    # Create database tables if they don't exist
    # Note: In production, use Alembic migrations instead
    if settings.ENVIRONMENT == "development":
        print("🗄️  Creating database tables (development mode)...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print("👋 Shutting down DealMoa API...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "딜모아 API 서버",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint with database connection test.
    Returns health status and database connectivity.
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }
