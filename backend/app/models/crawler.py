"""
Crawler management models: CrawlerRun, CrawlerError, CrawlerState
Tracks crawler execution, errors, and incremental state.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text,
    Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.models.database import Base
from app.models.base import TimestampMixin


class CrawlerStatus(str, enum.Enum):
    """Crawler execution status."""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Completed with some errors


class CrawlerRun(Base, TimestampMixin):
    """
    Crawler execution history and statistics.
    Tracks each crawl run for monitoring and debugging.
    """
    __tablename__ = "crawler_runs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("deal_sources.id"), nullable=False, index=True)

    # Execution info
    status = Column(
        SQLEnum(CrawlerStatus),
        nullable=False,
        default=CrawlerStatus.RUNNING,
        index=True
    )
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Statistics
    total_items_found = Column(Integer, nullable=False, default=0)
    new_items_created = Column(Integer, nullable=False, default=0)
    items_updated = Column(Integer, nullable=False, default=0)
    items_skipped = Column(Integer, nullable=False, default=0)
    errors_count = Column(Integer, nullable=False, default=0)

    # Execution details
    duration_seconds = Column(Integer, nullable=True)
    execution_metadata = Column(JSONB, nullable=True)  # Custom metadata

    # Relationships
    source = relationship("DealSource", back_populates="crawler_runs")
    errors = relationship("CrawlerError", back_populates="run", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_crawler_runs_source_started", "source_id", "started_at"),
        Index("idx_crawler_runs_status", "status", "started_at"),
    )

    def __repr__(self):
        return f"<CrawlerRun {self.id}: {self.status.value}>"


class CrawlerError(Base, TimestampMixin):
    """
    Detailed error logs for crawler debugging.
    Stores error messages and context for troubleshooting.
    """
    __tablename__ = "crawler_errors"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("crawler_runs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Error details
    error_type = Column(String(100), nullable=False)  # Exception class name
    error_message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)

    # Context
    url = Column(String(500), nullable=True)
    item_data = Column(JSONB, nullable=True)  # Item being processed when error occurred
    context = Column(JSONB, nullable=True)  # Additional context

    # Relationships
    run = relationship("CrawlerRun", back_populates="errors")

    # Indexes
    __table_args__ = (
        Index("idx_crawler_errors_run", "run_id", "created_at"),
        Index("idx_crawler_errors_type", "error_type", "created_at"),
    )

    def __repr__(self):
        return f"<CrawlerError {self.error_type}: {self.error_message[:50]}>"


class CrawlerState(Base, TimestampMixin):
    """
    Incremental crawl state (cursors, checkpoints).
    Stores state for resumable/incremental crawling.
    """
    __tablename__ = "crawler_state"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("deal_sources.id"), nullable=False, unique=True, index=True)

    # State data (flexible JSONB for different crawler implementations)
    state_data = Column(JSONB, nullable=False, default={})
    # Examples:
    # - {"last_page": 5, "last_post_id": "12345"}
    # - {"cursor": "abc123", "checkpoint": "2024-01-01T00:00:00Z"}

    last_successful_run_at = Column(DateTime, nullable=True)

    # Relationships
    source = relationship("DealSource")

    def __repr__(self):
        return f"<CrawlerState source_id={self.source_id}>"
