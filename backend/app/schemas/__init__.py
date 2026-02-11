"""
Pydantic schemas package.
Exports all schemas for API request/response validation.
"""

# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserKeywordBase,
    UserKeywordCreate,
    UserKeywordUpdate,
    UserKeywordResponse,
    UserKeywordListResponse,
    UserDeviceBase,
    UserDeviceCreate,
    UserDeviceUpdate,
    UserDeviceResponse,
)

# Deal schemas
from app.schemas.deal import (
    PriceSignal,
    DealSourceResponse,
    CategoryResponse,
    DealBase,
    DealCreate,
    DealUpdate,
    DealResponse,
    DealListResponse,
    DealDetailResponse,
    DealFeedParams,
    PriceHistoryResponse,
)

# Interaction schemas
from app.schemas.interaction import (
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
    BookmarkListResponse,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
)

# Crawler schemas
from app.schemas.crawler import (
    CrawlerRunResponse,
    CrawlerRunListResponse,
    CrawlerErrorResponse,
    CrawlerErrorListResponse,
    CrawlerStatsResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserKeywordBase",
    "UserKeywordCreate",
    "UserKeywordUpdate",
    "UserKeywordResponse",
    "UserKeywordListResponse",
    "UserDeviceBase",
    "UserDeviceCreate",
    "UserDeviceUpdate",
    "UserDeviceResponse",
    # Deal schemas
    "PriceSignal",
    "DealSourceResponse",
    "CategoryResponse",
    "DealBase",
    "DealCreate",
    "DealUpdate",
    "DealResponse",
    "DealListResponse",
    "DealDetailResponse",
    "DealFeedParams",
    "PriceHistoryResponse",
    # Interaction schemas
    "BookmarkCreate",
    "BookmarkUpdate",
    "BookmarkResponse",
    "BookmarkListResponse",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationMarkReadRequest",
    # Crawler schemas
    "CrawlerRunResponse",
    "CrawlerRunListResponse",
    "CrawlerErrorResponse",
    "CrawlerErrorListResponse",
    "CrawlerStatsResponse",
]
