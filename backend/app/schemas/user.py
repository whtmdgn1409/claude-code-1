"""
Pydantic schemas for User-related API requests and responses.
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from app.config import settings
from app.models.user import AuthProvider, Gender


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[Gender] = None


class UserCreate(BaseModel):
    """Schema for creating a new user via social auth."""
    auth_provider: AuthProvider
    auth_provider_id: str
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[Gender] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    auth_provider: AuthProvider
    push_enabled: bool
    dnd_enabled: bool
    dnd_start_time: time
    dnd_end_time: time
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRegisterRequest(BaseModel):
    """Schema for email/password registration."""
    email: EmailStr
    password: str = Field(..., min_length=settings.AUTH_PASSWORD_MIN_LENGTH)
    username: Optional[str] = None
    display_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Schema for email/password login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class UserSettingsUpdate(BaseModel):
    """Schema for updating notification settings only."""
    push_enabled: Optional[bool] = None
    dnd_enabled: Optional[bool] = None
    dnd_start_time: Optional[time] = None
    dnd_end_time: Optional[time] = None


# ============================================================================
# UserKeyword Schemas
# ============================================================================

class UserKeywordBase(BaseModel):
    """Base user keyword schema."""
    keyword: str = Field(..., min_length=1, max_length=100)
    is_inclusion: bool = True
    is_active: bool = True


class UserKeywordCreate(UserKeywordBase):
    """Schema for creating a new user keyword."""
    pass


class UserKeywordUpdate(BaseModel):
    """Schema for updating a user keyword."""
    is_active: Optional[bool] = None


class UserKeywordResponse(UserKeywordBase):
    """Schema for user keyword response."""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserKeywordListResponse(BaseModel):
    """Schema for list of user keywords."""
    keywords: List[UserKeywordResponse]
    total_count: int
    inclusion_count: int
    exclusion_count: int

    @validator('total_count', always=True)
    def validate_max_keywords(cls, v):
        """Enforce maximum 20 keywords per user."""
        if v > 20:
            raise ValueError('Maximum 20 keywords allowed per user')
        return v


# ============================================================================
# UserDevice Schemas
# ============================================================================

class UserDeviceBase(BaseModel):
    """Base user device schema."""
    device_type: str = Field(..., pattern='^(ios|android)$')
    device_token: str
    device_name: Optional[str] = None


class UserDeviceCreate(UserDeviceBase):
    """Schema for registering a new device."""
    pass


class UserDeviceUpdate(BaseModel):
    """Schema for updating device information."""
    device_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserDeviceResponse(UserDeviceBase):
    """Schema for device response."""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
