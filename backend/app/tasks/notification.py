"""
Celery tasks for push notification handling.
Manages notification scheduling, DND periods, and delivery.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from celery import Task

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.user import User
from app.models.deal import Deal
from app.models.interaction import Notification, NotificationStatus
from app.models.analytics import DealKeyword
from app.services.matcher import KeywordMatcher


class DatabaseTask(Task):
    """Base task with database session handling."""
    _db = None

    def after_return(self, *args, **kwargs):
        """Close database session after task completes."""
        if self._db is not None:
            self._db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=30,
    name="app.tasks.notification.send_push_notification"
)
def send_push_notification(self, user_id: int, deal_id: int) -> Dict[str, Any]:
    """
    Send push notification to a user about a matched deal.

    Process:
    1. Check if notification already sent (prevent duplicates)
    2. Check DND period
       - If in DND: Schedule for later (PENDING)
       - If not in DND: Send immediately (SENT)
    3. Create Notification record
    4. Send via FCM/APNS (Phase 2 - placeholder for now)

    Args:
        user_id: User ID to notify
        deal_id: Deal ID that matched

    Returns:
        Notification status dictionary
    """
    db = SessionLocal()
    self._db = db

    try:
        # Get user and deal
        user = db.query(User).filter(User.id == user_id).first()
        deal = db.query(Deal).filter(Deal.id == deal_id).first()

        if not user or not deal:
            return {
                "status": "failed",
                "error": "User or deal not found"
            }

        # Check if notification already exists (prevent duplicates)
        existing = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.deal_id == deal_id
        ).first()

        if existing:
            return {
                "status": "skipped",
                "reason": "duplicate",
                "notification_id": existing.id
            }

        # Get matched keywords for this user
        from app.models.user import UserKeyword
        user_keywords = db.query(UserKeyword.keyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True,
            UserKeyword.is_inclusion == True
        ).all()

        deal_keywords = db.query(DealKeyword.keyword).filter(
            DealKeyword.deal_id == deal_id
        ).all()

        user_kw_set = {kw.keyword.lower() for kw in user_keywords}
        deal_kw_set = {kw.keyword.lower() for kw in deal_keywords}

        matched_keywords = list(user_kw_set & deal_kw_set)

        # Create notification title and body
        title = f"🔥 {matched_keywords[0] if matched_keywords else '새로운'} 핫딜!"
        body = deal.title[:100]  # Truncate to 100 chars

        # Check DND period
        is_dnd = KeywordMatcher._is_in_dnd_period(user)

        if is_dnd:
            # Schedule for later
            scheduled_time = KeywordMatcher._calculate_scheduled_time(user)
            status = NotificationStatus.PENDING
            sent_at = None

            print(f"📅 Notification scheduled for {scheduled_time} (DND active)")
        else:
            # Send immediately
            status = NotificationStatus.SENT
            sent_at = datetime.utcnow()

            # TODO Phase 2: Actually send via FCM/APNS
            # For now, just mark as sent
            print(f"📤 Notification sent immediately to user {user_id}")

        # Create notification record
        notification = Notification(
            user_id=user_id,
            deal_id=deal_id,
            title=title,
            body=body,
            matched_keywords=matched_keywords,
            status=status,
            sent_at=sent_at
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return {
            "status": "success",
            "notification_id": notification.id,
            "is_dnd": is_dnd,
            "sent_immediately": not is_dnd
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Notification task failed: {e}")

        # Retry
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            # Create failed notification record
            notification = Notification(
                user_id=user_id,
                deal_id=deal_id,
                title="Notification Failed",
                body="",
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            db.add(notification)
            db.commit()

            return {
                "status": "failed",
                "error": str(e),
                "retries_exceeded": True
            }

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification.send_scheduled_notifications"
)
def send_scheduled_notifications(self) -> Dict[str, Any]:
    """
    Send pending notifications that are scheduled to be sent now.
    Runs every 10 minutes to check for notifications after DND period.

    Process:
    1. Find PENDING notifications with scheduled_for <= NOW
    2. Send via FCM/APNS (Phase 2 - placeholder)
    3. Update status to SENT

    Returns:
        Statistics dictionary
    """
    db = SessionLocal()
    self._db = db

    try:
        # Find pending notifications ready to send
        now = datetime.utcnow()

        # For Phase 1, we don't have scheduled_for field yet
        # So we'll just look for PENDING notifications from users not in DND
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING
        ).all()

        sent_count = 0

        for notification in pending_notifications:
            # Check if user is still in DND
            user = db.query(User).filter(User.id == notification.user_id).first()

            if not user:
                continue

            is_dnd = KeywordMatcher._is_in_dnd_period(user)

            if not is_dnd:
                # Send notification
                # TODO Phase 2: Actually send via FCM/APNS

                # Update status
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()

                sent_count += 1

        db.commit()

        print(f"✅ Sent {sent_count} scheduled notifications")

        return {
            "status": "success",
            "sent_count": sent_count
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Scheduled notification task failed: {e}")

        return {
            "status": "failed",
            "error": str(e)
        }

    finally:
        db.close()
