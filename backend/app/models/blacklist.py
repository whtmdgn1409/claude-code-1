"""
Content filtering model: Blacklist
Spam/advertiser filtering with regex support.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, Index
from app.models.database import Base
from app.models.base import TimestampMixin


class Blacklist(Base, TimestampMixin):
    """
    Spam/advertiser filtering rules.
    Supports keyword matching and regex patterns for blocking unwanted content.
    """
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)

    # Filter pattern
    pattern = Column(String(500), nullable=False, unique=True)
    pattern_type = Column(String(20), nullable=False, default="keyword")  # 'keyword' or 'regex'

    # Filter target
    target_field = Column(String(50), nullable=False, default="title")  # 'title', 'content', 'author'

    # Metadata
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Indexes
    __table_args__ = (
        Index("idx_blacklist_active", "is_active", "pattern_type"),
    )

    def __repr__(self):
        return f"<Blacklist {self.pattern_type}: {self.pattern}>"
