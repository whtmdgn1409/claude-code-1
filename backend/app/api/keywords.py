"""
API endpoints for user keyword management.
Handles CRUD operations for user interest and exclusion keywords.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserKeywordCreate,
    UserKeywordUpdate,
    UserKeywordResponse,
    UserKeywordListResponse
)
from app.services.keyword import KeywordService
from app.utils.auth import get_current_user


router = APIRouter(prefix="/api/v1/users/keywords", tags=["keywords"])


@router.post(
    "",
    response_model=UserKeywordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new keyword",
    description="Add a new interest or exclusion keyword for the current user. Maximum 20 keywords allowed."
)
def create_keyword(
    keyword_data: UserKeywordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new keyword for the authenticated user.

    - **keyword**: Keyword text (1-100 characters)
    - **is_inclusion**: True for interest keyword, False for exclusion keyword
    - **is_active**: Initial active status (default: True)

    **Limitations:**
    - Maximum 20 active keywords per user
    - No duplicate keywords allowed (case-insensitive)

    **Returns:**
    - 201 Created: Keyword successfully created
    - 400 Bad Request: Maximum keywords reached or duplicate keyword
    - 401 Unauthorized: Not authenticated
    """
    try:
        keyword = KeywordService.add_keyword(
            db=db,
            user_id=current_user.id,
            keyword=keyword_data.keyword,
            is_inclusion=keyword_data.is_inclusion
        )
        return UserKeywordResponse.model_validate(keyword)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/batch",
    response_model=UserKeywordListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add multiple keywords at once",
    description="Add multiple keywords in a single transaction (all or nothing)."
)
def create_keywords_batch(
    keywords_data: List[UserKeywordCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add multiple keywords for the authenticated user.

    **Transaction behavior:**
    - All keywords are added together or none at all
    - If any keyword fails validation, the entire operation is rolled back

    **Validations:**
    - Total active keywords (existing + new) must not exceed 20
    - No duplicates within the batch
    - No duplicates with existing keywords

    **Returns:**
    - 201 Created: All keywords successfully created
    - 400 Bad Request: Validation failed
    - 401 Unauthorized: Not authenticated
    """
    try:
        # Convert to list of dicts
        keywords_list = [
            {
                "keyword": kw.keyword,
                "is_inclusion": kw.is_inclusion
            }
            for kw in keywords_data
        ]

        created_keywords = KeywordService.add_keywords_batch(
            db=db,
            user_id=current_user.id,
            keywords=keywords_list
        )

        # Build response with counts
        inclusion_count = sum(1 for kw in created_keywords if kw.is_inclusion)
        exclusion_count = len(created_keywords) - inclusion_count

        return UserKeywordListResponse(
            keywords=[UserKeywordResponse.model_validate(kw) for kw in created_keywords],
            total_count=len(created_keywords),
            inclusion_count=inclusion_count,
            exclusion_count=exclusion_count
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=UserKeywordListResponse,
    summary="Get all keywords",
    description="Retrieve all active keywords for the current user, separated by type."
)
def get_keywords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active keywords for the authenticated user.

    **Returns:**
    - List of keywords separated by type (inclusion/exclusion)
    - Total count, inclusion count, and exclusion count
    - Ordered by creation date (newest first)

    **Response:**
    - 200 OK: Keywords retrieved successfully
    - 401 Unauthorized: Not authenticated
    """
    result = KeywordService.get_user_keywords(db=db, user_id=current_user.id)

    return UserKeywordListResponse(
        keywords=[UserKeywordResponse.model_validate(kw) for kw in result["keywords"]],
        total_count=result["total_count"],
        inclusion_count=result["inclusion_count"],
        exclusion_count=result["exclusion_count"]
    )


@router.put(
    "/{keyword_id}",
    response_model=UserKeywordResponse,
    summary="Update a keyword",
    description="Update a keyword's active status (enable/disable)."
)
def update_keyword(
    keyword_id: int,
    keyword_data: UserKeywordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a keyword for the authenticated user.

    **Currently supports:**
    - Toggling is_active status (enable/disable keyword)

    **Note:**
    - Disabled keywords don't count towards the 20-keyword limit
    - Disabled keywords won't trigger notifications

    **Returns:**
    - 200 OK: Keyword updated successfully
    - 400 Bad Request: Invalid data
    - 401 Unauthorized: Not authenticated
    - 404 Not Found: Keyword not found or access denied
    """
    if keyword_data.is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="is_active field is required"
        )

    try:
        updated_keyword = KeywordService.update_keyword(
            db=db,
            keyword_id=keyword_id,
            user_id=current_user.id,
            is_active=keyword_data.is_active
        )
        return UserKeywordResponse.model_validate(updated_keyword)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{keyword_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a keyword",
    description="Permanently delete a keyword."
)
def delete_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a keyword for the authenticated user.

    **Note:**
    - This is a hard delete (keyword is permanently removed)
    - Cannot be undone

    **Returns:**
    - 204 No Content: Keyword deleted successfully
    - 401 Unauthorized: Not authenticated
    - 404 Not Found: Keyword not found or access denied
    """
    try:
        KeywordService.delete_keyword(
            db=db,
            keyword_id=keyword_id,
            user_id=current_user.id
        )
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
