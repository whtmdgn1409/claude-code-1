"""
User-related models: User, UserKeyword, UserDevice
Handles authentication, personalization, and push notifications.
"""
from datetime import time
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Time, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.models.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class AuthProvider(str, enum.Enum):
    """Supported authentication providers."""
    KAKAO = "kakao"
    GOOGLE = "google"
    APPLE = "apple"


class Gender(str, enum.Enum):
    """User gender for demographic targeting (optional)."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    User accounts with social login and personalization settings.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    username = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    auth_provider = Column(SQLEnum(AuthProvider), nullable=False)
    auth_provider_id = Column(String(255), nullable=False)  # ID from OAuth provider

    # Profile
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Demographics (optional for personalized recommendations)
    age = Column(Integer, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)

    # Notification settings
    push_enabled = Column(Boolean, nullable=False, default=True)
    dnd_enabled = Column(Boolean, nullable=False, default=True)
    dnd_start_time = Column(Time, nullable=False, default=time(23, 0))  # 11:00 PM
    dnd_end_time = Column(Time, nullable=False, default=time(7, 0))     # 7:00 AM

    # Account status
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    keywords = relationship("UserKeyword", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        # Unique constraint on auth provider + provider ID
        UniqueConstraint("auth_provider", "auth_provider_id", name="uq_user_auth"),
        Index("idx_users_active", "is_active", "deleted_at"),
    )

    def __repr__(self):
        return f"<User {self.id}: {self.display_name or self.username}>"


class UserKeyword(Base, TimestampMixin):
    """
    User's interest keywords for personalized notifications.
    Supports both inclusion (interest) and exclusion (NOT) keywords.
    Maximum 20 keywords per user.
    """
    __tablename__ = "user_keywords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    keyword = Column(String(100), nullable=False)
    is_inclusion = Column(Boolean, nullable=False, default=True)  # True = include, False = exclude
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    user = relationship("User", back_populates="keywords")

    # Indexes
    __table_args__ = (
        Index("idx_user_keywords_active", "is_active", "keyword"),
        Index("idx_user_keywords_user_active", "user_id", "is_active"),
    )

    def __repr__(self):
        prefix = "" if self.is_inclusion else "NOT "
        return f"<UserKeyword {prefix}{self.keyword}>"


class UserDevice(Base, TimestampMixin):
    """
    User's devices for push notifications (FCM/APNS tokens).
    """
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    device_type = Column(String(20), nullable=False)  # 'ios', 'android'
    device_token = Column(String(500), nullable=False, unique=True)
    device_name = Column(String(100), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="devices")

    # Indexes
    __table_args__ = (
        Index("idx_user_devices_active", "user_id", "is_active"),
    )

    def __repr__(self):
        return f"<UserDevice {self.device_type}: {self.device_name or 'Unknown'}>"
