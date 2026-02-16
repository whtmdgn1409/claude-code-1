"""
Notification management service.
Handles querying, reading, and clicking notifications for users.
"""
from typing import Dict, List, Optional
from datetime import datetime
from math import ceil
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.interaction import Notification, NotificationStatus
from app.models.deal import Deal


class NotificationService:
    """Service class for managing user notifications."""

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get paginated notifications for a user with deal eager loading.

        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Dictionary with notifications, pagination info, and unread_count
        """
        base_query = db.query(Notification).options(
            joinedload(Notification.deal).joinedload(Deal.source)
        ).filter(
            Notification.user_id == user_id
        )

        # Get total count
        total = base_query.count()

        # Get unread count
        unread_count = NotificationService.get_unread_count(db, user_id)

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        notifications = base_query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(page_size).all()

        return {
            "notifications": notifications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "unread_count": unread_count
        }

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """
        Get count of unread notifications for a user.
        A notification is unread if read_at is NULL and status is SENT or DELIVERED.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of unread notifications
        """
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read_at == None,
            Notification.status.in_([
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED
            ])
        ).count()

    @staticmethod
    def mark_as_read(
        db: Session,
        user_id: int,
        notification_ids: List[int]
    ) -> int:
        """
        Mark specific notifications as read with ownership verification.

        Args:
            db: Database session
            user_id: User ID (ownership check)
            notification_ids: List of notification IDs to mark as read

        Returns:
            Number of notifications updated
        """
        now = datetime.utcnow()
        updated = db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id,
            Notification.read_at == None
        ).update(
            {"read_at": now},
            synchronize_session="fetch"
        )

        db.commit()
        return updated

    @staticmethod
    def mark_as_clicked(
        db: Session,
        user_id: int,
        notification_id: int
    ) -> Optional[Notification]:
        """
        Mark a notification as clicked (user tapped to view the deal).

        Args:
            db: Database session
            user_id: User ID (ownership check)
            notification_id: Notification ID

        Returns:
            Updated Notification object, or None if not found/not owned
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return None

        now = datetime.utcnow()
        notification.status = NotificationStatus.CLICKED
        if not notification.clicked_at:
            notification.clicked_at = now
        if not notification.read_at:
            notification.read_at = now

        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """
        Mark all unread notifications as read for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of notifications updated
        """
        now = datetime.utcnow()
        updated = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read_at == None
        ).update(
            {"read_at": now},
            synchronize_session="fetch"
        )

        db.commit()
        return updated
