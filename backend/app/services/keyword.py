"""
Keyword management service for user interest keywords.
Handles business logic for adding, retrieving, updating, and deleting keywords.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import UserKeyword


class KeywordService:
    """Service class for managing user keywords."""

    @staticmethod
    def add_keyword(
        db: Session,
        user_id: int,
        keyword: str,
        is_inclusion: bool = True
    ) -> UserKeyword:
        """
        Add a new keyword for a user.

        Args:
            db: Database session
            user_id: User ID
            keyword: Keyword text
            is_inclusion: True for inclusion keyword, False for exclusion

        Returns:
            Created UserKeyword object

        Raises:
            ValueError: If maximum keywords (20) reached or duplicate keyword found
        """
        # Normalize keyword
        normalized_keyword = KeywordService._normalize_keyword(keyword)

        if not normalized_keyword:
            raise ValueError("Keyword cannot be empty")

        # Check current active keyword count
        active_count = db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True
        ).count()

        if active_count >= 20:
            raise ValueError("Maximum 20 keywords allowed per user")

        # Check for duplicates
        if KeywordService._check_duplicate(db, user_id, normalized_keyword):
            raise ValueError(f"Duplicate keyword: {keyword}")

        # Create new keyword
        new_keyword = UserKeyword(
            user_id=user_id,
            keyword=normalized_keyword,
            is_inclusion=is_inclusion,
            is_active=True
        )

        db.add(new_keyword)
        db.commit()
        db.refresh(new_keyword)

        return new_keyword

    @staticmethod
    def add_keywords_batch(
        db: Session,
        user_id: int,
        keywords: List[Dict]
    ) -> List[UserKeyword]:
        """
        Add multiple keywords at once (all or nothing transaction).

        Args:
            db: Database session
            user_id: User ID
            keywords: List of dicts with 'keyword' and 'is_inclusion' keys

        Returns:
            List of created UserKeyword objects

        Raises:
            ValueError: If total would exceed 20 or any duplicate found
        """
        # Check current count
        current_count = db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True
        ).count()

        # Validate total count after addition
        if current_count + len(keywords) > 20:
            raise ValueError(
                f"Cannot add {len(keywords)} keywords. "
                f"Current: {current_count}, Max: 20"
            )

        # Normalize and validate all keywords first
        normalized_keywords = []
        for kw_data in keywords:
            keyword = kw_data.get('keyword', '')
            normalized = KeywordService._normalize_keyword(keyword)

            if not normalized:
                raise ValueError(f"Keyword cannot be empty")

            # Check for duplicates
            if KeywordService._check_duplicate(db, user_id, normalized):
                raise ValueError(f"Duplicate keyword: {keyword}")

            # Check for duplicates within the batch
            if normalized in normalized_keywords:
                raise ValueError(f"Duplicate keyword in batch: {keyword}")

            normalized_keywords.append(normalized)

        # Create all keywords
        created_keywords = []
        for i, kw_data in enumerate(keywords):
            new_keyword = UserKeyword(
                user_id=user_id,
                keyword=normalized_keywords[i],
                is_inclusion=kw_data.get('is_inclusion', True),
                is_active=True
            )
            db.add(new_keyword)
            created_keywords.append(new_keyword)

        # Commit all at once
        db.commit()

        # Refresh all objects
        for kw in created_keywords:
            db.refresh(kw)

        return created_keywords

    @staticmethod
    def get_user_keywords(db: Session, user_id: int) -> Dict:
        """
        Get all active keywords for a user, separated by type.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with keywords list and counts
        """
        # Query all active keywords
        keywords = db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True
        ).order_by(UserKeyword.created_at.desc()).all()

        # Separate by type
        inclusion_keywords = [kw for kw in keywords if kw.is_inclusion]
        exclusion_keywords = [kw for kw in keywords if not kw.is_inclusion]

        return {
            "keywords": keywords,
            "total_count": len(keywords),
            "inclusion_count": len(inclusion_keywords),
            "exclusion_count": len(exclusion_keywords)
        }

    @staticmethod
    def get_keyword_by_id(
        db: Session,
        keyword_id: int,
        user_id: int
    ) -> Optional[UserKeyword]:
        """
        Get a specific keyword by ID, with ownership verification.

        Args:
            db: Database session
            keyword_id: Keyword ID
            user_id: User ID (for ownership verification)

        Returns:
            UserKeyword object if found and owned by user, None otherwise
        """
        keyword = db.query(UserKeyword).filter(
            UserKeyword.id == keyword_id,
            UserKeyword.user_id == user_id
        ).first()

        return keyword

    @staticmethod
    def update_keyword(
        db: Session,
        keyword_id: int,
        user_id: int,
        is_active: bool
    ) -> UserKeyword:
        """
        Update a keyword's active status.

        Args:
            db: Database session
            keyword_id: Keyword ID
            user_id: User ID (for ownership verification)
            is_active: New active status

        Returns:
            Updated UserKeyword object

        Raises:
            ValueError: If keyword not found or not owned by user
        """
        keyword = KeywordService.get_keyword_by_id(db, keyword_id, user_id)

        if not keyword:
            raise ValueError("Keyword not found or access denied")

        keyword.is_active = is_active
        db.commit()
        db.refresh(keyword)

        return keyword

    @staticmethod
    def delete_keyword(
        db: Session,
        keyword_id: int,
        user_id: int
    ) -> None:
        """
        Delete a keyword (hard delete).

        Args:
            db: Database session
            keyword_id: Keyword ID
            user_id: User ID (for ownership verification)

        Raises:
            ValueError: If keyword not found or not owned by user
        """
        keyword = KeywordService.get_keyword_by_id(db, keyword_id, user_id)

        if not keyword:
            raise ValueError("Keyword not found or access denied")

        db.delete(keyword)
        db.commit()

    @staticmethod
    def _normalize_keyword(keyword: str) -> str:
        """
        Normalize a keyword for consistent storage and comparison.
        - Strips leading/trailing whitespace
        - Converts to lowercase
        - Collapses multiple spaces to single space

        Args:
            keyword: Raw keyword string

        Returns:
            Normalized keyword string

        Example:
            "  맥북 프로  " -> "맥북 프로"
            "MACBOOK" -> "macbook"
        """
        # Strip, lowercase, and collapse multiple spaces
        normalized = " ".join(keyword.lower().strip().split())
        return normalized

    @staticmethod
    def _check_duplicate(
        db: Session,
        user_id: int,
        normalized_keyword: str
    ) -> bool:
        """
        Check if a normalized keyword already exists for the user.
        Case-insensitive comparison on normalized keywords.

        Args:
            db: Database session
            user_id: User ID
            normalized_keyword: Already normalized keyword

        Returns:
            True if duplicate exists, False otherwise
        """
        existing = db.query(UserKeyword).filter(
            UserKeyword.user_id == user_id,
            UserKeyword.is_active == True,
            func.lower(UserKeyword.keyword) == normalized_keyword
        ).first()

        return existing is not None
