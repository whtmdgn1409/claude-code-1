"""
Keyword matching engine for personalized deal recommendations.
Matches deals to users based on inclusion/exclusion keywords with DND support.
"""
from typing import List, Dict
from datetime import datetime, timedelta, time as datetime_time
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, exists
from math import ceil

from app.models.deal import Deal
from app.models.user import User, UserKeyword
from app.models.analytics import DealKeyword


class KeywordMatcher:
    """Service class for keyword-based deal matching."""

    @staticmethod
    def match_deal_to_users(db: Session, deal: Deal) -> List[User]:
        """
        Find users who should be notified about a new deal.

        Algorithm:
        1. Extract deal keywords
        2. Find users with matching inclusion keywords (OR condition)
        3. Filter out users with matching exclusion keywords (AND NOT condition)
        4. Check DND periods for notification scheduling

        Args:
            db: Database session
            deal: Deal object to match

        Returns:
            List of User objects who should receive notifications
        """
        # Get all keywords for this deal
        deal_keywords_query = db.query(DealKeyword.keyword).filter(
            DealKeyword.deal_id == deal.id
        )
        deal_keywords_list = [kw.keyword.lower() for kw in deal_keywords_query.all()]

        if not deal_keywords_list:
            return []

        # Find users with matching inclusion keywords
        # Use EXISTS subquery for better performance
        from sqlalchemy import select

        inclusion_subquery = select(UserKeyword.user_id).filter(
            UserKeyword.is_active == True,
            UserKeyword.is_inclusion == True,
            func.lower(UserKeyword.keyword).in_(deal_keywords_list)
        ).distinct().scalar_subquery()

        # Get users with matching inclusion keywords
        potential_users_query = db.query(User).filter(
            User.id.in_(inclusion_subquery),
            User.is_active == True,
            User.push_enabled == True,
            User.deleted_at == None
        )

        potential_users = potential_users_query.all()

        # Filter out users with matching exclusion keywords
        matched_users = []
        for user in potential_users:
            # Get user's exclusion keywords
            exclusion_keywords = db.query(UserKeyword.keyword).filter(
                UserKeyword.user_id == user.id,
                UserKeyword.is_active == True,
                UserKeyword.is_inclusion == False
            ).all()

            exclusion_keywords_lower = [kw.keyword.lower() for kw in exclusion_keywords]

            # Check if any deal keyword matches exclusion keywords
            has_exclusion = any(
                kw in deal_keywords_list
                for kw in exclusion_keywords_lower
            )

            if not has_exclusion:
                matched_users.append(user)

        return matched_users

    @staticmethod
    def match_user_to_deals(
        db: Session,
        user: User,
        page: int = 1,
        page_size: int = 20,
        days: int = 7
    ) -> Dict:
        """
        Get personalized deal feed for a user based on their keywords.

        Algorithm:
        1. Get user's active inclusion keywords
        2. Find deals with matching keywords (OR condition)
        3. Filter out deals with matching exclusion keywords
        4. Apply time filter (recent N days)
        5. Sort by hot_score DESC
        6. Paginate results

        Args:
            db: Database session
            user: User object
            page: Page number (1-indexed)
            page_size: Number of items per page
            days: Number of days to look back (default: 7)

        Returns:
            Dictionary with deals, pagination info
        """
        # Get user's active inclusion keywords
        inclusion_keywords = db.query(UserKeyword.keyword).filter(
            UserKeyword.user_id == user.id,
            UserKeyword.is_active == True,
            UserKeyword.is_inclusion == True
        ).all()

        inclusion_keywords_lower = [kw.keyword.lower() for kw in inclusion_keywords]

        if not inclusion_keywords_lower:
            # No keywords set, return empty result
            return {
                "deals": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

        # Get user's exclusion keywords
        exclusion_keywords = db.query(UserKeyword.keyword).filter(
            UserKeyword.user_id == user.id,
            UserKeyword.is_active == True,
            UserKeyword.is_inclusion == False
        ).all()

        exclusion_keywords_lower = [kw.keyword.lower() for kw in exclusion_keywords]

        # Calculate time filter
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Base query with eager loading to prevent N+1
        base_query = db.query(Deal).options(
            joinedload(Deal.source),
            joinedload(Deal.category)
        ).filter(
            Deal.is_active == True,
            Deal.is_blocked == False,
            Deal.deleted_at == None,
            Deal.published_at >= cutoff_date
        )

        # Filter by inclusion keywords using EXISTS subquery
        # A deal must have at least one matching keyword
        inclusion_exists = exists().where(
            and_(
                DealKeyword.deal_id == Deal.id,
                func.lower(DealKeyword.keyword).in_(inclusion_keywords_lower)
            )
        )

        base_query = base_query.filter(inclusion_exists)

        # Filter out deals with exclusion keywords if any
        if exclusion_keywords_lower:
            exclusion_exists = exists().where(
                and_(
                    DealKeyword.deal_id == Deal.id,
                    func.lower(DealKeyword.keyword).in_(exclusion_keywords_lower)
                )
            )
            base_query = base_query.filter(~exclusion_exists)

        # Get total count before pagination
        total = base_query.count()

        # Apply sorting and pagination
        offset = (page - 1) * page_size
        deals = base_query.order_by(
            Deal.hot_score.desc()
        ).offset(offset).limit(page_size).all()

        return {
            "deals": deals,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total > 0 else 0
        }

    @staticmethod
    def _is_in_dnd_period(user: User) -> bool:
        """
        Check if current time is within user's DND period.
        Handles overnight DND periods (e.g., 23:00 - 07:00).

        Args:
            user: User object with DND settings

        Returns:
            True if currently in DND period, False otherwise
        """
        if not user.dnd_enabled:
            return False

        now = datetime.now().time()
        dnd_start = user.dnd_start_time
        dnd_end = user.dnd_end_time

        # Handle overnight DND (e.g., 23:00 - 07:00)
        if dnd_start > dnd_end:
            # DND spans midnight
            return now >= dnd_start or now < dnd_end
        else:
            # Normal DND period
            return dnd_start <= now < dnd_end

    @staticmethod
    def _calculate_scheduled_time(user: User) -> datetime:
        """
        Calculate when to send notification after DND period ends.

        Args:
            user: User object with DND settings

        Returns:
            Scheduled datetime for notification
        """
        now = datetime.now()
        dnd_end = user.dnd_end_time

        # Create datetime for today's DND end time
        scheduled_today = datetime.combine(now.date(), dnd_end)

        # If DND end time has already passed today, schedule for tomorrow
        if now.time() >= dnd_end:
            scheduled_today += timedelta(days=1)

        return scheduled_today
