from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.models.database import engine, get_db, init_db
from app.models import Base

# Import all models to ensure they're registered
from app.models.deal import DealSource, Category, Deal
from app.models.user import User, UserKeyword, UserDevice
from app.models.interaction import Bookmark, Notification
from app.models.analytics import PriceHistory, DealStatistics, DealKeyword
from app.models.crawler import CrawlerRun, CrawlerError, CrawlerState
from app.models.blacklist import Blacklist

# Import API routers
from app.api.deals import router as deals_router
from app.api.users import router as users_router
from app.api.keywords import router as keywords_router
from app.api.bookmarks import router as bookmarks_router
from app.api.matched_deals import router as matched_deals_router
from app.api.notifications import router as notifications_router


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

# Register API routers
app.include_router(deals_router)
app.include_router(users_router)
app.include_router(keywords_router)
app.include_router(bookmarks_router)
app.include_router(matched_deals_router)
app.include_router(notifications_router)


@app.on_event("startup")
async def startup_event():
    """Application startup event - initialize database."""
    print("🚀 Starting DealMoa API...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🛠 AUTO_CREATE_SCHEMA: {settings.AUTO_CREATE_SCHEMA}")
    print(f"🐞 DEBUG: {settings.DEBUG}")

    # Create database tables if they don't exist.
    # In production, set AUTO_CREATE_SCHEMA=true only for bootstrap/new DB initialization.
    if settings.ENVIRONMENT == "development" or settings.AUTO_CREATE_SCHEMA:
        print("🗄️  Ensuring database tables exist...")
        try:
            init_db()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️ Database bootstrap failed: {e}")


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
