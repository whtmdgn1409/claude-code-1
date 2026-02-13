"""
Celery tasks for push notification handling.
Manages notification scheduling, DND periods, and delivery via FCM.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from celery import Task
from sqlalchemy.exc import IntegrityError

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.user import User, UserKeyword
from app.models.deal import Deal
from app.models.interaction import Notification, NotificationStatus
from app.models.analytics import DealKeyword
from app.services.matcher import KeywordMatcher
from app.services.device import DeviceService
from app.services.fcm import FCMService


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
    1. Check DND period
       - If in DND: Create notification with scheduled_for, status PENDING
       - If not in DND: Send immediately via FCM
    2. Create Notification record (unique constraint prevents duplicates)
    3. Send via FCM (or dry-run if not configured)

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

        # Get matched keywords for this user
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
            # Schedule for after DND
            scheduled_time = KeywordMatcher._calculate_scheduled_time(user)
            status = NotificationStatus.PENDING
            sent_at = None
            push_response = None
            print(f"📅 Notification scheduled for {scheduled_time} (DND active)")
        else:
            # Send immediately via FCM
            scheduled_time = None
            status = NotificationStatus.SENT
            sent_at = datetime.utcnow()

            # Get user's device tokens and send
            device_tokens = DeviceService.get_active_device_tokens(db, user_id)
            if device_tokens:
                fcm_data = {"deal_id": str(deal_id), "type": "keyword_match"}
                push_response = FCMService.send_to_multiple_devices(
                    device_tokens=device_tokens,
                    title=title,
                    body=body,
                    data=fcm_data
                )
            else:
                push_response = {"skipped": True, "reason": "no_devices"}
                print(f"⚠️ No active devices for user {user_id}, notification saved only")

            print(f"📤 Notification sent to user {user_id} ({len(device_tokens)} devices)")

        # Create notification record
        notification = Notification(
            user_id=user_id,
            deal_id=deal_id,
            title=title,
            body=body,
            matched_keywords=matched_keywords,
            status=status,
            scheduled_for=scheduled_time,
            sent_at=sent_at,
            push_response=push_response
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

    except IntegrityError:
        db.rollback()
        return {
            "status": "skipped",
            "reason": "duplicate",
            "user_id": user_id,
            "deal_id": deal_id
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Notification task failed: {e}")

        # Retry
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            # Create failed notification record
            try:
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
            except IntegrityError:
                db.rollback()

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
    Runs periodically to check for notifications after DND period.

    Process:
    1. Find PENDING notifications with scheduled_for <= NOW
    2. Send via FCM (or dry-run)
    3. Update status to SENT

    Returns:
        Statistics dictionary
    """
    db = SessionLocal()
    self._db = db

    try:
        now = datetime.utcnow()

        # Find pending notifications ready to send
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING,
            Notification.scheduled_for != None,
            Notification.scheduled_for <= now
        ).all()

        sent_count = 0
        failed_count = 0

        for notification in pending_notifications:
            # Get user's device tokens
            device_tokens = DeviceService.get_active_device_tokens(db, notification.user_id)

            if device_tokens:
                fcm_data = {"deal_id": str(notification.deal_id), "type": "scheduled"}
                push_response = FCMService.send_to_multiple_devices(
                    device_tokens=device_tokens,
                    title=notification.title,
                    body=notification.body,
                    data=fcm_data
                )
                notification.push_response = push_response
            else:
                push_response = {"skipped": True, "reason": "no_devices"}
                notification.push_response = push_response

            # Update status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            notification.scheduled_for = None
            sent_count += 1

        db.commit()

        print(f"✅ Sent {sent_count} scheduled notifications")

        return {
            "status": "success",
            "sent_count": sent_count,
            "failed_count": failed_count
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
