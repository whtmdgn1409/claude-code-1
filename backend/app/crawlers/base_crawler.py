"""
Base crawler class for all deal source crawlers.
Provides common functionality for crawling, error handling, and state management.
"""
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import CrawlerRun, CrawlerError, CrawlerState, CrawlerStatus, Deal, DealSource
from app.config import settings


class BaseCrawler(ABC):
    """
    Base class for all crawlers.
    Implements common crawling patterns and error handling.
    """

    def __init__(self, db: Session, source_name: str):
        """
        Initialize crawler.

        Args:
            db: Database session
            source_name: Name of the deal source (e.g., "ppomppu")
        """
        self.db = db
        self.source_name = source_name
        self.source = self._get_or_create_source()
        self.crawler_run: Optional[CrawlerRun] = None
        self.stats = {
            "total_found": 0,
            "new_created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

    def _get_or_create_source(self) -> DealSource:
        """Get or create the deal source from database."""
        source = self.db.query(DealSource).filter_by(name=self.source_name).first()
        if not source:
            raise ValueError(f"Deal source '{self.source_name}' not found in database")
        return source

    def _start_crawler_run(self) -> CrawlerRun:
        """Start a new crawler run and save to database."""
        run = CrawlerRun(
            source_id=self.source.id,
            status=CrawlerStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.commit()
        return run

    def _complete_crawler_run(self, status: CrawlerStatus):
        """Mark crawler run as complete."""
        if self.crawler_run:
            self.crawler_run.status = status
            self.crawler_run.completed_at = datetime.utcnow()
            self.crawler_run.total_items_found = self.stats["total_found"]
            self.crawler_run.new_items_created = self.stats["new_created"]
            self.crawler_run.items_updated = self.stats["updated"]
            self.crawler_run.items_skipped = self.stats["skipped"]
            self.crawler_run.errors_count = self.stats["errors"]

            # Calculate duration
            if self.crawler_run.started_at:
                duration = (
                    self.crawler_run.completed_at - self.crawler_run.started_at
                ).total_seconds()
                self.crawler_run.duration_seconds = int(duration)

            self.db.commit()

    def _log_error(self, error_type: str, error_message: str, url: str = None, item_data: Dict = None):
        """Log an error to the database."""
        if self.crawler_run:
            error = CrawlerError(
                run_id=self.crawler_run.id,
                error_type=error_type,
                error_message=error_message,
                traceback=traceback.format_exc(),
                url=url,
                item_data=item_data,
            )
            self.db.add(error)
            self.db.commit()
            self.stats["errors"] += 1

    def _get_crawler_state(self) -> Dict:
        """Get saved crawler state from database."""
        state = self.db.query(CrawlerState).filter_by(source_id=self.source.id).first()
        if state:
            return state.state_data or {}
        return {}

    def _save_crawler_state(self, state_data: Dict):
        """Save crawler state to database."""
        state = self.db.query(CrawlerState).filter_by(source_id=self.source.id).first()
        if state:
            state.state_data = state_data
            state.last_successful_run_at = datetime.utcnow()
        else:
            state = CrawlerState(
                source_id=self.source.id,
                state_data=state_data,
                last_successful_run_at=datetime.utcnow(),
            )
            self.db.add(state)
        self.db.commit()

    def _save_deal(self, deal_data: Dict[str, Any]) -> Optional[Deal]:
        """
        Save or update a deal in the database.

        Args:
            deal_data: Dictionary with deal information

        Returns:
            Created or updated Deal object, or None if skipped
        """
        try:
            # Check if deal already exists
            existing_deal = (
                self.db.query(Deal)
                .filter_by(
                    source_id=self.source.id,
                    external_id=deal_data["external_id"]
                )
                .first()
            )

            if existing_deal:
                # Update existing deal metrics
                existing_deal.upvotes = deal_data.get("upvotes", existing_deal.upvotes)
                existing_deal.downvotes = deal_data.get("downvotes", existing_deal.downvotes)
                existing_deal.comment_count = deal_data.get("comment_count", existing_deal.comment_count)
                existing_deal.view_count = deal_data.get("view_count", existing_deal.view_count)

                # Recalculate hot score
                existing_deal.calculate_hot_score()

                self.db.commit()
                self.stats["updated"] += 1
                return existing_deal
            else:
                # Create new deal
                deal = Deal(
                    source_id=self.source.id,
                    **deal_data
                )

                # Calculate initial hot score
                deal.calculate_hot_score()

                self.db.add(deal)
                self.db.commit()
                self.stats["new_created"] += 1
                return deal

        except IntegrityError as e:
            self.db.rollback()
            self._log_error(
                "IntegrityError",
                str(e),
                url=deal_data.get("url"),
                item_data=deal_data
            )
            self.stats["skipped"] += 1
            return None
        except Exception as e:
            self.db.rollback()
            self._log_error(
                type(e).__name__,
                str(e),
                url=deal_data.get("url"),
                item_data=deal_data
            )
            return None

    def _respect_rate_limit(self):
        """Sleep to respect rate limiting."""
        time.sleep(settings.CRAWLER_REQUEST_DELAY)

    @abstractmethod
    def fetch_deals(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch deals from the source website.
        Must be implemented by subclasses.

        Args:
            max_pages: Maximum number of pages to crawl

        Returns:
            List of deal dictionaries
        """
        pass

    @abstractmethod
    def parse_deal(self, raw_data: Any) -> Optional[Dict[str, Any]]:
        """
        Parse raw deal data into structured format.
        Must be implemented by subclasses.

        Args:
            raw_data: Raw data from website (e.g., BeautifulSoup element)

        Returns:
            Parsed deal dictionary or None if parsing failed
        """
        pass

    def run(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        Main crawling entry point.

        Args:
            max_pages: Maximum number of pages to crawl

        Returns:
            Statistics dictionary
        """
        print(f"🚀 Starting crawler for {self.source.display_name}...")

        # Start crawler run
        self.crawler_run = self._start_crawler_run()

        try:
            # Fetch and process deals
            deals = self.fetch_deals(max_pages=max_pages)
            self.stats["total_found"] = len(deals)

            print(f"📦 Found {len(deals)} deals")

            for deal_data in deals:
                self._save_deal(deal_data)
                self._respect_rate_limit()

            # Mark as successful
            self._complete_crawler_run(
                CrawlerStatus.SUCCESS if self.stats["errors"] == 0
                else CrawlerStatus.PARTIAL
            )

            print(f"✅ Crawler completed successfully!")
            print(f"   - New: {self.stats['new_created']}")
            print(f"   - Updated: {self.stats['updated']}")
            print(f"   - Skipped: {self.stats['skipped']}")
            print(f"   - Errors: {self.stats['errors']}")

        except Exception as e:
            print(f"❌ Crawler failed: {e}")
            self._log_error(type(e).__name__, str(e))
            self._complete_crawler_run(CrawlerStatus.FAILED)
            raise

        return self.stats
