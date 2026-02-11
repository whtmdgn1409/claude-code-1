"""
Base model class with common fields and mixins.
All models inherit from TimestampMixin for created_at/updated_at tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow
        )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality via deleted_at column."""

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True, default=None)

    def soft_delete(self):
        """Mark this record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if record is soft-deleted."""
        return self.deleted_at is not None
