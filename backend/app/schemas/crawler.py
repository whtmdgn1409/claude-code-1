"""
Pydantic schemas for crawler-related responses (admin/monitoring use).
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.crawler import CrawlerStatus


# ============================================================================
# CrawlerRun Schemas
# ============================================================================

class CrawlerRunResponse(BaseModel):
    """Schema for crawler run response."""
    id: int
    source_id: int
    status: CrawlerStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_items_found: int
    new_items_created: int
    items_updated: int
    items_skipped: int
    errors_count: int
    duration_seconds: Optional[int] = None
    execution_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CrawlerRunListResponse(BaseModel):
    """Schema for paginated crawler runs."""
    runs: List[CrawlerRunResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# CrawlerError Schemas
# ============================================================================

class CrawlerErrorResponse(BaseModel):
    """Schema for crawler error response."""
    id: int
    run_id: int
    error_type: str
    error_message: str
    traceback: Optional[str] = None
    url: Optional[str] = None
    item_data: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlerErrorListResponse(BaseModel):
    """Schema for paginated crawler errors."""
    errors: List[CrawlerErrorResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Crawler Statistics Schemas
# ============================================================================

class CrawlerStatsResponse(BaseModel):
    """Schema for crawler statistics summary."""
    total_runs: int
    successful_runs: int
    failed_runs: int
    total_items_created: int
    total_errors: int
    avg_duration_seconds: Optional[float] = None
    last_run_at: Optional[datetime] = None
