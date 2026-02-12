"""
API endpoints for bookmark management.
Handles CRUD operations for user bookmarks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.interaction import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkListResponse
)
from app.schemas.deal import DealResponse
from app.services.bookmark import BookmarkService
from app.utils.auth import get_current_user


router = APIRouter(prefix="/api/v1/bookmarks", tags=["bookmarks"])


@router.post(
    "",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a bookmark",
    description="Bookmark a deal for the current user."
)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new bookmark for the authenticated user.

    - **deal_id**: ID of the deal to bookmark
    - **notes**: Optional user notes about the bookmark

    **Returns:**
    - 201 Created: Bookmark successfully created
    - 400 Bad Request: Deal not found or already bookmarked
    - 401 Unauthorized: Not authenticated
    """
    try:
        bookmark = BookmarkService.add_bookmark(
            db=db,
            user_id=current_user.id,
            deal_id=bookmark_data.deal_id,
            notes=bookmark_data.notes
        )
        return BookmarkResponse.model_validate(bookmark)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=BookmarkListResponse,
    summary="Get bookmarks",
    description="Retrieve all bookmarks for the current user with pagination."
)
def get_bookmarks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated bookmarks for the authenticated user.

    **Returns:**
    - List of bookmarks with deal information
    - Ordered by creation date (newest first)
    - Includes pagination metadata

    **Response:**
    - 200 OK: Bookmarks retrieved successfully
    - 401 Unauthorized: Not authenticated
    """
    result = BookmarkService.get_user_bookmarks(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    # Build response with deal info
    bookmarks_with_deals = []
    for bookmark in result["bookmarks"]:
        bookmark_dict = {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "deal_id": bookmark.deal_id,
            "notes": bookmark.notes,
            "created_at": bookmark.created_at
        }

        # Include deal information if available
        if bookmark.deal:
            bookmark_dict["deal"] = DealResponse.model_validate(bookmark.deal).model_dump()

        bookmarks_with_deals.append(BookmarkResponse(**bookmark_dict))

    return BookmarkListResponse(
        bookmarks=bookmarks_with_deals,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )


@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bookmark",
    description="Remove a bookmark."
)
def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a bookmark for the authenticated user.

    **Note:**
    - This is a hard delete (bookmark is permanently removed)
    - Decrements the deal's bookmark count

    **Returns:**
    - 204 No Content: Bookmark deleted successfully
    - 401 Unauthorized: Not authenticated
    - 404 Not Found: Bookmark not found or access denied
    """
    try:
        BookmarkService.delete_bookmark(
            db=db,
            bookmark_id=bookmark_id,
            user_id=current_user.id
        )
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
