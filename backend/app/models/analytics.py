"""
Analytics and tracking models: PriceHistory, DealStatistics, DealKeyword
Supports price signals and keyword matching.
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Index, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.base import TimestampMixin


class PriceHistory(Base, TimestampMixin):
    """
    Historical price data for price signal calculation.
    Tracks price changes over time for each product.
    """
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)

    # Product identification (may be same product from different deals)
    mall_name = Column(String(100), nullable=True)
    mall_product_id = Column(String(255), nullable=True, index=True)
    product_name = Column(String(500), nullable=True)

    # Price data
    price = Column(Integer, nullable=False)
    original_price = Column(Integer, nullable=True)
    discount_rate = Column(Float, nullable=True)

    # Timestamp
    recorded_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    deal = relationship("Deal", back_populates="price_history")

    # Indexes
    __table_args__ = (
        # Index for product price history lookups
        Index("idx_price_history_product", "mall_product_id", "recorded_at"),
        Index("idx_price_history_deal_recorded", "deal_id", "recorded_at"),
    )

    def __repr__(self):
        return f"<PriceHistory {self.product_name}: ₩{self.price:,}>"


class DealStatistics(Base, TimestampMixin):
    """
    Time-series engagement snapshots for trend analysis.
    Captures engagement metrics at different points in time.
    """
    __tablename__ = "deal_statistics"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)

    # Snapshot metrics
    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    bookmark_count = Column(Integer, nullable=False, default=0)
    hot_score = Column(Float, nullable=False, default=0.0)

    # Snapshot timestamp
    snapshot_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    deal = relationship("Deal", back_populates="statistics")

    # Indexes
    __table_args__ = (
        Index("idx_deal_stats_snapshot", "deal_id", "snapshot_at"),
    )

    def __repr__(self):
        return f"<DealStatistics deal={self.deal_id} at {self.snapshot_at}>"


class DealKeyword(Base, TimestampMixin):
    """
    Denormalized keyword table for fast keyword matching.
    Extracted from deal titles and content for real-time notifications.
    """
    __tablename__ = "deal_keywords"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)

    keyword = Column(String(100), nullable=False, index=True)
    source = Column(String(20), nullable=False)  # 'title', 'content', 'product_name'

    # Relationships
    deal = relationship("Deal", back_populates="keywords")

    # Indexes
    __table_args__ = (
        # Primary index for keyword matching queries
        Index("idx_deal_keywords_keyword", "keyword", "deal_id"),
        Index("idx_deal_keywords_deal", "deal_id"),
    )

    def __repr__(self):
        return f"<DealKeyword {self.keyword} (deal={self.deal_id})>"
