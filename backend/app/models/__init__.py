"""
SQLAlchemy models package.
Exports all models for Alembic auto-detection and application use.
"""
from app.models.database import Base, get_db, init_db, drop_db, engine, SessionLocal

# Import all models for Alembic auto-detection
from app.models.base import TimestampMixin, SoftDeleteMixin

from app.models.deal import DealSource, Category, Deal
from app.models.user import User, UserKeyword, UserDevice, AuthProvider, Gender
from app.models.interaction import Bookmark, Notification, NotificationStatus
from app.models.analytics import PriceHistory, DealStatistics, DealKeyword
from app.models.crawler import CrawlerRun, CrawlerError, CrawlerState, CrawlerStatus
from app.models.blacklist import Blacklist

# Export all models
__all__ = [
    # Database
    "Base",
    "get_db",
    "init_db",
    "drop_db",
    "engine",
    "SessionLocal",
    # Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    # Deal models
    "DealSource",
    "Category",
    "Deal",
    # User models
    "User",
    "UserKeyword",
    "UserDevice",
    "AuthProvider",
    "Gender",
    # Interaction models
    "Bookmark",
    "Notification",
    "NotificationStatus",
    # Analytics models
    "PriceHistory",
    "DealStatistics",
    "DealKeyword",
    # Crawler models
    "CrawlerRun",
    "CrawlerError",
    "CrawlerState",
    "CrawlerStatus",
    # Blacklist model
    "Blacklist",
]
