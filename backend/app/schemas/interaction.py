"""
Pydantic schemas for user interaction API requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.interaction import NotificationStatus


# ============================================================================
# Bookmark Schemas
# ============================================================================

class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark."""
    deal_id: int
    notes: Optional[str] = None


class BookmarkUpdate(BaseModel):
    """Schema for updating bookmark notes."""
    notes: Optional[str] = None


class BookmarkResponse(BaseModel):
    """Schema for bookmark response."""
    id: int
    user_id: int
    deal_id: int
    notes: Optional[str] = None
    created_at: datetime

    # Optional: include deal info
    deal: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """Schema for paginated bookmark list."""
    bookmarks: List[BookmarkResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Notification Schemas
# ============================================================================

class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    user_id: int
    deal_id: Optional[int] = None
    title: str
    body: str
    matched_keywords: Optional[List[str]] = None
    status: NotificationStatus
    scheduled_for: Optional[datetime] = None
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationUnreadCountResponse(BaseModel):
    """Schema for unread notification count."""
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read/clicked."""
    notification_ids: List[int]


# ============================================================================
# Device Schemas
# ============================================================================

class DeviceRegisterRequest(BaseModel):
    """Schema for registering a device for push notifications."""
    device_type: str  # 'ios' or 'android'
    device_token: str
    device_name: Optional[str] = None


class DeviceUnregisterRequest(BaseModel):
    """Schema for unregistering a device."""
    device_token: str


class DeviceResponse(BaseModel):
    """Schema for device response."""
    id: int
    user_id: int
    device_type: str
    device_token: str
    device_name: Optional[str] = None
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema for device list response."""
    devices: List[DeviceResponse]
    total: int
