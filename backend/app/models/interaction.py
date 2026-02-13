"""
User interaction models: Bookmark, Notification
Tracks user engagement with deals.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Index, UniqueConstraint, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.models.database import Base
from app.models.base import TimestampMixin


class NotificationStatus(str, enum.Enum):
    """Push notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CLICKED = "clicked"


class Bookmark(Base, TimestampMixin):
    """
    User's saved/bookmarked deals.
    """
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)

    notes = Column(Text, nullable=True)  # Optional user notes

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    deal = relationship("Deal", back_populates="bookmarks")

    # Constraints
    __table_args__ = (
        # User can only bookmark a deal once
        UniqueConstraint("user_id", "deal_id", name="uq_bookmark_user_deal"),
        Index("idx_bookmarks_user_created", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<Bookmark user={self.user_id} deal={self.deal_id}>"


class Notification(Base, TimestampMixin):
    """
    Push notification history and delivery tracking.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="SET NULL"), nullable=True, index=True)

    # Notification content
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    matched_keywords = Column(JSONB, nullable=True)  # Keywords that triggered this notification

    # Delivery tracking
    status = Column(
        SQLEnum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True
    )
    scheduled_for = Column(DateTime, nullable=True)  # DND scheduled delivery time
    read_at = Column(DateTime, nullable=True)  # When user read the notification
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # FCM/APNS response
    push_response = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
    deal = relationship("Deal", back_populates="notifications")

    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint("user_id", "deal_id", name="uq_notification_user_deal"),
        Index("idx_notifications_user_created", "user_id", "created_at"),
        Index("idx_notifications_status_created", "status", "created_at"),
        Index("idx_notifications_scheduled", "status", "scheduled_for"),
    )

    def __repr__(self):
        return f"<Notification {self.id}: {self.title[:30]}>"
