"""
Database utility functions.
Helper functions for common database operations.
"""
from contextlib import contextmanager
from typing import Generator, List, Any
from sqlalchemy.orm import Session
from app.models.database import SessionLocal


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def bulk_insert(db: Session, model_class: Any, data_list: List[dict]) -> int:
    """
    Bulk insert records into database.

    Args:
        db: Database session
        model_class: SQLAlchemy model class
        data_list: List of dictionaries with model data

    Returns:
        Number of records inserted

    Usage:
        deals_data = [
            {"title": "Deal 1", "price": 10000, ...},
            {"title": "Deal 2", "price": 20000, ...},
        ]
        count = bulk_insert(db, Deal, deals_data)
    """
    if not data_list:
        return 0

    instances = [model_class(**data) for data in data_list]
    db.bulk_save_objects(instances)
    db.commit()
    return len(instances)


def bulk_update(db: Session, model_class: Any, updates: List[dict]) -> int:
    """
    Bulk update records in database.

    Args:
        db: Database session
        model_class: SQLAlchemy model class
        updates: List of dictionaries with {id: ..., field1: value1, ...}

    Returns:
        Number of records updated

    Usage:
        updates = [
            {"id": 1, "hot_score": 150.0},
            {"id": 2, "hot_score": 200.0},
        ]
        count = bulk_update(db, Deal, updates)
    """
    if not updates:
        return 0

    db.bulk_update_mappings(model_class, updates)
    db.commit()
    return len(updates)


def paginate(query, page: int = 1, page_size: int = 20):
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (items, total_count, total_pages)

    Usage:
        query = db.query(Deal).filter(Deal.is_active == True)
        deals, total, total_pages = paginate(query, page=2, page_size=20)
    """
    total = query.count()
    total_pages = (total + page_size - 1) // page_size

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total, total_pages


def execute_raw_sql(db: Session, sql: str, params: dict = None) -> Any:
    """
    Execute raw SQL query.

    Args:
        db: Database session
        sql: SQL query string
        params: Optional parameters for query

    Returns:
        Query result

    Usage:
        result = execute_raw_sql(db, "SELECT COUNT(*) FROM deals WHERE is_active = :active", {"active": True})
    """
    return db.execute(sql, params or {})
