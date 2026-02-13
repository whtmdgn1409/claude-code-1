"""
Device management service for push notification tokens.
Handles registration, deactivation, and querying of user devices.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import UserDevice


class DeviceService:
    """Service class for managing user device tokens."""

    @staticmethod
    def register_device(
        db: Session,
        user_id: int,
        device_type: str,
        device_token: str,
        device_name: Optional[str] = None
    ) -> UserDevice:
        """
        Register a device token for push notifications.
        If the same token exists for a different user, deactivate it first.
        If the same token exists for this user, reactivate it.

        Args:
            db: Database session
            user_id: User ID
            device_type: 'ios' or 'android'
            device_token: FCM/APNS device token
            device_name: Optional device name

        Returns:
            Created or updated UserDevice object
        """
        # Check if token already exists
        existing = db.query(UserDevice).filter(
            UserDevice.device_token == device_token
        ).first()

        if existing:
            if existing.user_id == user_id:
                # Same user, reactivate and update
                existing.is_active = True
                existing.device_name = device_name or existing.device_name
                existing.last_used_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
            else:
                # Different user owns this token → deactivate old
                existing.is_active = False
                db.flush()

        # Create new device record
        device = UserDevice(
            user_id=user_id,
            device_type=device_type,
            device_token=device_token,
            device_name=device_name,
            is_active=True,
            last_used_at=datetime.utcnow()
        )

        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def unregister_device(
        db: Session,
        user_id: int,
        device_token: str
    ) -> bool:
        """
        Deactivate a device token (soft delete).

        Args:
            db: Database session
            user_id: User ID (for ownership verification)
            device_token: Device token to deactivate

        Returns:
            True if device was found and deactivated, False otherwise
        """
        device = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.device_token == device_token,
            UserDevice.is_active == True
        ).first()

        if not device:
            return False

        device.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_user_devices(db: Session, user_id: int) -> List[UserDevice]:
        """
        Get all active devices for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of active UserDevice objects
        """
        return db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.is_active == True
        ).order_by(UserDevice.last_used_at.desc()).all()

    @staticmethod
    def get_active_device_tokens(db: Session, user_id: int) -> List[str]:
        """
        Get all active device tokens for a user (for FCM sending).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of active device token strings
        """
        devices = db.query(UserDevice.device_token).filter(
            UserDevice.user_id == user_id,
            UserDevice.is_active == True
        ).all()

        return [d.device_token for d in devices]
