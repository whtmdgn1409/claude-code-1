"""
Bookmark management service.
Handles business logic for adding, retrieving, and deleting bookmarks.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from math import ceil

from app.models.interaction import Bookmark
from app.models.deal import Deal


class BookmarkService:
    """Service class for managing user bookmarks."""

    @staticmethod
    def add_bookmark(
        db: Session,
        user_id: int,
        deal_id: int,
        notes: Optional[str] = None
    ) -> Bookmark:
        """
        Add a new bookmark for a user.

        Args:
            db: Database session
            user_id: User ID
            deal_id: Deal ID to bookmark
            notes: Optional user notes

        Returns:
            Created Bookmark object

        Raises:
            ValueError: If deal doesn't exist or already bookmarked
        """
        # Check if deal exists
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.deleted_at == None
        ).first()

        if not deal:
            raise ValueError("Deal not found")

        # Create new bookmark
        new_bookmark = Bookmark(
            user_id=user_id,
            deal_id=deal_id,
            notes=notes
        )

        try:
            db.add(new_bookmark)

            # Increment bookmark count
            deal.bookmark_count += 1

            db.commit()
            db.refresh(new_bookmark)

            return new_bookmark

        except IntegrityError:
            db.rollback()
            raise ValueError("Already bookmarked")

    @staticmethod
    def get_user_bookmarks(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get paginated bookmarks for a user with deal information.

        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Dictionary with bookmarks, pagination info
        """
        # Base query with eager loading to prevent N+1
        query = db.query(Bookmark).options(
            joinedload(Bookmark.deal).joinedload(Deal.source),
            joinedload(Bookmark.deal).joinedload(Deal.category)
        ).filter(
            Bookmark.user_id == user_id
        )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        bookmarks = query.order_by(
            Bookmark.created_at.desc()
        ).offset(offset).limit(page_size).all()

        return {
            "bookmarks": bookmarks,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if total > 0 else 0
        }

    @staticmethod
    def delete_bookmark(
        db: Session,
        bookmark_id: int,
        user_id: int
    ) -> None:
        """
        Delete a bookmark with ownership verification.

        Args:
            db: Database session
            bookmark_id: Bookmark ID
            user_id: User ID (for ownership verification)

        Raises:
            ValueError: If bookmark not found or not owned by user
        """
        bookmark = db.query(Bookmark).filter(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == user_id
        ).first()

        if not bookmark:
            raise ValueError("Bookmark not found or access denied")

        # Decrement bookmark count
        deal = db.query(Deal).filter(Deal.id == bookmark.deal_id).first()
        if deal and deal.bookmark_count > 0:
            deal.bookmark_count -= 1

        db.delete(bookmark)
        db.commit()

    @staticmethod
    def check_is_bookmarked(
        db: Session,
        user_id: int,
        deal_id: int
    ) -> bool:
        """
        Check if a deal is bookmarked by a user.

        Args:
            db: Database session
            user_id: User ID
            deal_id: Deal ID

        Returns:
            True if bookmarked, False otherwise
        """
        exists = db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.deal_id == deal_id
        ).first() is not None

        return exists
