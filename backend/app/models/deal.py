"""
Deal-related models: DealSource, Category, Deal
Core domain models for hot deal aggregation.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class DealSource(Base, TimestampMixin):
    """
    Korean community sites we crawl for hot deals.
    Examples: 뽐뿌 (Ppomppu), 루리웹 (Ruliweb), 펨코 (Fmkorea), etc.
    """
    __tablename__ = "deal_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "ppomppu"
    display_name = Column(String(100), nullable=False)  # e.g., "뽐뿌"
    base_url = Column(String(255), nullable=False)
    color_code = Column(String(7), nullable=False)  # Hex color for UI badges
    is_active = Column(Boolean, nullable=False, default=True)
    crawl_interval_minutes = Column(Integer, nullable=False, default=5)

    # Relationships
    deals = relationship("Deal", back_populates="source")
    crawler_runs = relationship("CrawlerRun", back_populates="source")

    def __repr__(self):
        return f"<DealSource {self.display_name}>"


class Category(Base, TimestampMixin):
    """
    Product categories for auto-classification.
    Examples: 전자제품, 패션/의류, 식품/음료, etc.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Hierarchical relationship
    parent = relationship("Category", remote_side=[id], backref="children")
    deals = relationship("Deal", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Deal(Base, TimestampMixin, SoftDeleteMixin):
    """
    Hot deals from all sources.
    Central table with prices, engagement metrics, and hot scores.
    """
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    # Source information
    source_id = Column(Integer, ForeignKey("deal_sources.id"), nullable=False, index=True)
    external_id = Column(String(255), nullable=False)  # Original post ID from source site
    url = Column(String(500), nullable=False)

    # Content fields
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    # Product information
    product_name = Column(String(500), nullable=True)
    mall_name = Column(String(100), nullable=True)  # Shopping mall name
    mall_product_url = Column(String(500), nullable=True)
    mall_product_id = Column(String(255), nullable=True, index=True)

    # Pricing
    price = Column(Integer, nullable=True)  # Current price in KRW
    original_price = Column(Integer, nullable=True)  # Original price before discount
    discount_rate = Column(Float, nullable=True)  # Discount percentage
    price_signal = Column(String(20), nullable=True)  # 'lowest', 'average', 'high'

    # Engagement metrics
    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    bookmark_count = Column(Integer, nullable=False, default=0)

    # Computed fields
    hot_score = Column(Float, nullable=False, default=0.0, index=True)

    # AI-generated summary
    ai_summary = Column(Text, nullable=True)  # 3-line summary
    ai_summary_generated_at = Column(DateTime, nullable=True)  # AI summary generation timestamp

    # Comments data
    comments = Column(JSON, nullable=True)  # Comment data as JSON array
    comments_fetched_at = Column(DateTime, nullable=True)  # Comment fetch timestamp

    # Classification
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)

    # Status flags
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_blocked = Column(Boolean, nullable=False, default=False)  # Blocked by blacklist
    block_reason = Column(String(255), nullable=True)

    # Timestamps
    published_at = Column(DateTime, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    source = relationship("DealSource", back_populates="deals")
    category = relationship("Category", back_populates="deals")
    bookmarks = relationship("Bookmark", back_populates="deal", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="deal", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="deal", cascade="all, delete-orphan")
    statistics = relationship("DealStatistics", back_populates="deal", cascade="all, delete-orphan")
    keywords = relationship("DealKeyword", back_populates="deal", cascade="all, delete-orphan")

    # Indexes and constraints
    __table_args__ = (
        # Unique constraint on source + external_id
        UniqueConstraint("source_id", "external_id", name="uq_deal_source_external_id"),

        # Index for feed queries (most frequent query pattern)
        Index(
            "idx_deals_feed",
            "is_active", "published_at", "hot_score",
            postgresql_where=text("deleted_at IS NULL AND is_blocked = false")
        ),

        # Index for Korean text search using trigram
        Index(
            "idx_deals_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"}
        ),

        # Index for product name search
        Index(
            "idx_deals_product_trgm",
            "product_name",
            postgresql_using="gin",
            postgresql_ops={"product_name": "gin_trgm_ops"}
        ),

        # Index for category filtering
        Index("idx_deals_category_published", "category_id", "published_at"),
    )

    @hybrid_property
    def age_hours(self):
        """Calculate age of deal in hours."""
        if self.published_at:
            return (datetime.utcnow() - self.published_at).total_seconds() / 3600
        return 0

    @property
    def engagement_score(self):
        """Calculate engagement score (upvotes - downvotes + comments)."""
        return (self.upvotes - self.downvotes) + self.comment_count

    def calculate_hot_score(self):
        """
        Calculate hot score using weighted engagement with time decay.
        Formula: (upvotes - downvotes) * 10 + comment_count * 5 + (view_count / 100) - (age_hours * 0.5)
        """
        age = self.age_hours
        score = (
            (self.upvotes - self.downvotes) * 10 +
            self.comment_count * 5 +
            (self.view_count / 100) -
            (age * 0.5)
        )
        self.hot_score = max(0, score)  # Ensure non-negative
        return self.hot_score

    def __repr__(self):
        return f"<Deal {self.id}: {self.title[:50]}>"
