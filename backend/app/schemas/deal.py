"""
Pydantic schemas for Deal-related API requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
import enum


# ============================================================================
# Enums
# ============================================================================

class PriceSignal(str, enum.Enum):
    """Price signal indicators."""
    LOWEST = "lowest"    # 🟢 역대가 (all-time low)
    AVERAGE = "average"  # 🟡 평균가 (average price)
    HIGH = "high"        # 🔴 비쌈 (expensive)


# ============================================================================
# DealSource Schemas
# ============================================================================

class DealSourceResponse(BaseModel):
    """Schema for deal source response."""
    id: int
    name: str
    display_name: str
    base_url: str
    color_code: str
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# Deal Schemas
# ============================================================================

class DealBase(BaseModel):
    """Base deal schema with common fields."""
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    product_name: Optional[str] = None
    mall_name: Optional[str] = None
    mall_product_url: Optional[HttpUrl] = None
    price: Optional[int] = Field(None, ge=0)
    original_price: Optional[int] = Field(None, ge=0)
    discount_rate: Optional[float] = Field(None, ge=0, le=100)


class DealCreate(DealBase):
    """Schema for creating a new deal (internal crawler use)."""
    source_id: int
    external_id: str
    url: str
    published_at: datetime
    upvotes: int = 0
    downvotes: int = 0
    comment_count: int = 0
    view_count: int = 0


class DealUpdate(BaseModel):
    """Schema for updating deal metrics."""
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    comment_count: Optional[int] = None
    view_count: Optional[int] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None


class DealResponse(DealBase):
    """Schema for deal response."""
    id: int
    source_id: int
    url: str

    # Engagement metrics
    upvotes: int
    downvotes: int
    comment_count: int
    view_count: int
    bookmark_count: int
    hot_score: float

    # Price signal
    price_signal: Optional[PriceSignal] = None

    # AI summary
    ai_summary: Optional[str] = None

    # Category
    category_id: Optional[int] = None

    # Status
    is_active: bool

    # Timestamps
    published_at: datetime
    created_at: datetime

    # Relationships (optional, can be included via joins)
    source: Optional[DealSourceResponse] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


class DealListResponse(BaseModel):
    """Schema for paginated deal list response."""
    deals: List[DealResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DealDetailResponse(DealResponse):
    """Schema for detailed deal response with additional info."""
    # Include full content
    # Add price history (last 30 days)
    price_history: Optional[List[Dict[str, Any]]] = None

    # User-specific fields (if authenticated)
    is_bookmarked: Optional[bool] = None


# ============================================================================
# Feed Query Schemas
# ============================================================================

class DealFeedParams(BaseModel):
    """Query parameters for deal feed."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    source_id: Optional[int] = None
    category_id: Optional[int] = None
    keyword: Optional[str] = None
    sort_by: str = Field("hot_score", pattern="^(hot_score|published_at|price|bookmark_count)$")
    order: str = Field("desc", pattern="^(asc|desc)$")


# ============================================================================
# Price History Schemas
# ============================================================================

class PriceHistoryResponse(BaseModel):
    """Schema for price history response."""
    id: int
    deal_id: int
    price: int
    original_price: Optional[int] = None
    discount_rate: Optional[float] = None
    recorded_at: datetime

    class Config:
        from_attributes = True
