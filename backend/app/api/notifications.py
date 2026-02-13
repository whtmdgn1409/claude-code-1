"""
API endpoints for notification and device management.
Handles notification listing, read/click tracking, and device token registration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.interaction import (
    NotificationResponse,
    NotificationListResponse,
    NotificationUnreadCountResponse,
    NotificationMarkReadRequest,
    DeviceRegisterRequest,
    DeviceUnregisterRequest,
    DeviceResponse,
    DeviceListResponse,
)
from app.services.notification import NotificationService
from app.services.device import DeviceService
from app.utils.auth import get_current_user


router = APIRouter(prefix="/api/v1", tags=["notifications"])


# ============================================================================
# Notification Endpoints
# ============================================================================

@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    summary="Get notifications",
    description="Retrieve paginated notifications for the current user."
)
def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated notifications for the authenticated user.

    Returns notifications ordered by creation date (newest first),
    along with unread count and pagination metadata.
    """
    result = NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    notifications = [
        NotificationResponse.model_validate(n) for n in result["notifications"]
    ]

    return NotificationListResponse(
        notifications=notifications,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        unread_count=result["unread_count"]
    )


@router.get(
    "/notifications/unread-count",
    response_model=NotificationUnreadCountResponse,
    summary="Get unread count",
    description="Get the number of unread notifications."
)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the unread notification count for the authenticated user."""
    count = NotificationService.get_unread_count(db, current_user.id)
    return NotificationUnreadCountResponse(unread_count=count)


@router.post(
    "/notifications/read",
    summary="Mark notifications as read",
    description="Mark specific notifications as read."
)
def mark_notifications_read(
    request: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark specific notifications as read.

    Only notifications owned by the current user will be updated.
    """
    updated = NotificationService.mark_as_read(
        db=db,
        user_id=current_user.id,
        notification_ids=request.notification_ids
    )
    return {"updated": updated}


@router.post(
    "/notifications/read-all",
    summary="Mark all as read",
    description="Mark all notifications as read."
)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read for the current user."""
    updated = NotificationService.mark_all_as_read(db, current_user.id)
    return {"updated": updated}


@router.post(
    "/notifications/{notification_id}/click",
    response_model=NotificationResponse,
    summary="Click notification",
    description="Mark a notification as clicked (user viewed the deal)."
)
def click_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as clicked.

    Sets status to CLICKED and records clicked_at timestamp.
    Also marks as read if not already read.
    """
    notification = NotificationService.mark_as_clicked(
        db=db,
        user_id=current_user.id,
        notification_id=notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return NotificationResponse.model_validate(notification)


# ============================================================================
# Device Endpoints
# ============================================================================

@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register device",
    description="Register a device for push notifications."
)
def register_device(
    request: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a device token for push notifications.

    If the same token is already registered to another user,
    it will be transferred to the current user.
    """
    device = DeviceService.register_device(
        db=db,
        user_id=current_user.id,
        device_type=request.device_type,
        device_token=request.device_token,
        device_name=request.device_name
    )
    return DeviceResponse.model_validate(device)


@router.delete(
    "/devices",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister device",
    description="Unregister a device from push notifications."
)
def unregister_device(
    request: DeviceUnregisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister a device token (soft delete).

    The device will no longer receive push notifications.
    """
    success = DeviceService.unregister_device(
        db=db,
        user_id=current_user.id,
        device_token=request.device_token
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or already inactive"
        )

    return None


@router.get(
    "/devices",
    response_model=DeviceListResponse,
    summary="List devices",
    description="List all active devices for the current user."
)
def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active devices for the authenticated user."""
    devices = DeviceService.get_user_devices(db, current_user.id)
    return DeviceListResponse(
        devices=[DeviceResponse.model_validate(d) for d in devices],
        total=len(devices)
    )
