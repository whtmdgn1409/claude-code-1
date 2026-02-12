"""
API endpoints for personalized matched deals.
Provides keyword-based deal recommendations for authenticated users.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.deal import DealListResponse, DealResponse
from app.services.matcher import KeywordMatcher
from app.utils.auth import get_current_user


router = APIRouter(prefix="/api/v1/users/matched-deals", tags=["matched-deals"])


@router.get(
    "",
    response_model=DealListResponse,
    summary="Get personalized matched deals",
    description="Get deals matched to user's keywords with pagination."
)
def get_matched_deals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized deal feed based on user's keywords.

    **Matching Algorithm:**
    - Inclusion keywords (OR): At least one must match
    - Exclusion keywords (AND NOT): None must match
    - Sorted by hot_score (descending)

    **Parameters:**
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **days**: Look back N days (default: 7, max: 30)

    **Returns:**
    - Paginated list of matched deals
    - Only deals from recent N days
    - Sorted by popularity (hot_score)

    **Response:**
    - 200 OK: Matched deals retrieved successfully
    - 401 Unauthorized: Not authenticated

    **Note:**
    - Returns empty list if user has no active inclusion keywords
    - Respects user's exclusion keywords (NOT conditions)
    """
    result = KeywordMatcher.match_user_to_deals(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
        days=days
    )

    return DealListResponse(
        deals=[DealResponse.model_validate(deal) for deal in result["deals"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )
