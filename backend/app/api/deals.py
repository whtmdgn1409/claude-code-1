"""
Deal API endpoints.
Provides endpoints for listing, searching, and viewing deals.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func, or_, text
from math import ceil

from app.models.database import get_db
from app.models.deal import Deal, DealSource, Category
from app.schemas.deal import (
    DealResponse,
    DealListResponse,
    DealDetailResponse,
    DealSourceResponse,
    CategoryResponse
)

router = APIRouter(prefix="/api/v1", tags=["deals"])


# ============================================================================
# Deal List Endpoint
# ============================================================================

@router.get("/deals", response_model=DealListResponse)
async def get_deals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    source_id: Optional[int] = Query(None, description="Filter by deal source ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    sort_by: str = Query("hot_score", regex="^(hot_score|published_at|price|bookmark_count)$", description="Sort field"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of deals.

    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 20, max: 100)
    - **source_id**: Filter by deal source (optional)
    - **category_id**: Filter by category (optional)
    - **sort_by**: Sort by field (hot_score, published_at, price, bookmark_count)
    - **order**: Sort order (asc, desc)
    """
    # Base query with filters
    query = db.query(Deal).options(
        joinedload(Deal.source),
        joinedload(Deal.category)
    ).filter(
        Deal.is_active == True,
        Deal.is_blocked == False,
        Deal.deleted_at == None
    )

    # Apply filters
    if source_id:
        query = query.filter(Deal.source_id == source_id)

    if category_id:
        query = query.filter(Deal.category_id == category_id)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(Deal, sort_by)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * page_size
    deals = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return DealListResponse(
        deals=deals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# Deal Search Endpoint
# ============================================================================
# NOTE: This must come BEFORE the /deals/{deal_id} endpoint to avoid route conflicts

@router.get("/deals/search", response_model=DealListResponse)
async def search_deals(
    keyword: str = Query(..., min_length=2, description="Search keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    source_id: Optional[int] = Query(None, description="Filter by deal source ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    """
    Search deals by keyword using PostgreSQL full-text search with pg_trgm.

    - **keyword**: Search keyword (min 2 characters)
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 20, max: 100)
    - **source_id**: Filter by deal source (optional)
    - **category_id**: Filter by category (optional)
    """
    # Base query with LIKE-based search for Korean text compatibility
    query = db.query(Deal).options(
        joinedload(Deal.source),
        joinedload(Deal.category)
    ).filter(
        Deal.is_active == True,
        Deal.is_blocked == False,
        Deal.deleted_at == None,
        or_(
            Deal.title.contains(keyword),  # LIKE %keyword%
            Deal.product_name.contains(keyword)
        )
    )

    # Apply filters
    if source_id:
        query = query.filter(Deal.source_id == source_id)

    if category_id:
        query = query.filter(Deal.category_id == category_id)

    # Get total count before pagination
    total = query.count()

    # Sort by relevance (hot_score as proxy for relevance)
    query = query.order_by(desc(Deal.hot_score))

    # Apply pagination
    offset = (page - 1) * page_size
    deals = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return DealListResponse(
        deals=deals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# Deal Detail Endpoint
# ============================================================================

@router.get("/deals/{deal_id}", response_model=DealDetailResponse)
async def get_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific deal.

    - **deal_id**: The ID of the deal to retrieve
    """
    deal = db.query(Deal).options(
        joinedload(Deal.source),
        joinedload(Deal.category),
        joinedload(Deal.price_history)
    ).filter(
        Deal.id == deal_id,
        Deal.deleted_at == None
    ).first()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Format price history for response
    price_history = []
    if deal.price_history:
        price_history = [
            {
                "price": ph.price,
                "original_price": ph.original_price,
                "discount_rate": ph.discount_rate,
                "recorded_at": ph.recorded_at.isoformat()
            }
            for ph in sorted(deal.price_history, key=lambda x: x.recorded_at, reverse=True)[:30]
        ]

    # Convert to response model
    response = DealDetailResponse.model_validate(deal)
    response.price_history = price_history

    return response


# ============================================================================
# Deal Sources Endpoint
# ============================================================================

@router.get("/sources", response_model=List[DealSourceResponse])
async def get_deal_sources(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get list of all deal sources (communities).

    - **is_active**: Filter by active status (optional)
    """
    query = db.query(DealSource)

    if is_active is not None:
        query = query.filter(DealSource.is_active == is_active)

    sources = query.order_by(DealSource.id).all()

    return sources


# ============================================================================
# Categories Endpoint
# ============================================================================

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get list of all categories.

    - **is_active**: Filter by active status (optional)
    """
    query = db.query(Category)

    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    categories = query.order_by(Category.id).all()

    return categories
