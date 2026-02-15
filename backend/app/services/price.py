"""
Price tracking and signal calculation service.
Handles historical price data analysis and price signal generation.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.analytics import PriceHistory
from app.models.deal import Deal


# Price signal calculation constants
LOWEST_THRESHOLD = 0.05   # 역대가 판정 기준 (±5%)
AVERAGE_THRESHOLD = 0.10  # 평균가 판정 기준 (±10%)
MIN_HISTORY_RECORDS = 3   # 최소 히스토리 개수
HISTORY_DAYS = 90         # 분석 기간 (90일)


class PriceService:
    """Service class for price tracking and signal calculation."""

    @staticmethod
    def calculate_price_signal(db: Session, deal: Deal) -> Optional[str]:
        """
        Calculate price signal based on historical price data.

        Args:
            db: Database session
            deal: Deal object to calculate signal for

        Returns:
            Price signal: 'lowest' (🟢), 'average' (🟡), 'high' (🔴), or None

        Algorithm:
            1. Query last 90 days of price history
            2. Require minimum 3 records
            3. Calculate min_price and avg_price
            4. Determine signal:
               - current_price ≤ min_price × 1.05 → 'lowest'
               - current_price ≤ avg_price × 1.10 → 'average'
               - otherwise → 'high'
        """
        # No price to analyze
        if not deal.price:
            return None

        # Query recent price history
        cutoff_date = datetime.utcnow() - timedelta(days=HISTORY_DAYS)

        history_query = db.query(PriceHistory).filter(
            PriceHistory.deal_id == deal.id,
            PriceHistory.recorded_at >= cutoff_date
        )

        # Check minimum record requirement
        record_count = history_query.count()
        if record_count < MIN_HISTORY_RECORDS:
            return None

        # Calculate statistics
        stats = history_query.with_entities(
            func.min(PriceHistory.price).label('min_price'),
            func.avg(PriceHistory.price).label('avg_price')
        ).first()

        if not stats or not stats.min_price or not stats.avg_price:
            return None

        min_price = float(stats.min_price)
        avg_price = float(stats.avg_price)
        current_price = float(deal.price)

        # Determine signal
        if current_price <= min_price * (1 + LOWEST_THRESHOLD):
            return 'lowest'
        elif current_price <= avg_price * (1 + AVERAGE_THRESHOLD):
            return 'average'
        else:
            return 'high'

    @staticmethod
    def get_price_statistics(db: Session, deal: Deal) -> Dict:
        """
        Get comprehensive price statistics for a deal.

        Args:
            db: Database session
            deal: Deal object

        Returns:
            Dictionary with keys:
            - lowest: Minimum price in history
            - highest: Maximum price in history
            - average: Average price
            - current: Current price
            - record_count: Number of price records
        """
        # Query all price history for the deal
        history_query = db.query(PriceHistory).filter(
            PriceHistory.deal_id == deal.id
        )

        record_count = history_query.count()

        # No history available
        if record_count == 0:
            return {
                'lowest': deal.price,
                'highest': deal.price,
                'average': deal.price,
                'current': deal.price,
                'record_count': 0
            }

        # Calculate statistics
        stats = history_query.with_entities(
            func.min(PriceHistory.price).label('min_price'),
            func.max(PriceHistory.price).label('max_price'),
            func.avg(PriceHistory.price).label('avg_price')
        ).first()

        return {
            'lowest': int(stats.min_price) if stats.min_price else deal.price,
            'highest': int(stats.max_price) if stats.max_price else deal.price,
            'average': int(stats.avg_price) if stats.avg_price else deal.price,
            'current': deal.price,
            'record_count': record_count
        }

    @staticmethod
    def update_deal_price_signal(db: Session, deal_id: int) -> bool:
        """
        Update price_signal field for a specific deal.

        Args:
            db: Database session
            deal_id: Deal ID to update

        Returns:
            True if updated successfully, False if deal not found
        """
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.deleted_at == None
        ).first()

        if not deal:
            return False

        # Calculate and update signal
        new_signal = PriceService.calculate_price_signal(db, deal)
        deal.price_signal = new_signal

        db.commit()
        return True
