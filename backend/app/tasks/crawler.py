"""
Celery tasks for automated crawling.
Runs crawlers periodically and triggers keyword matching.
"""
from typing import Dict, Any
from celery import Task

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.crawlers.ppomppu import PpomppuCrawler
from app.services.keyword_extractor import KeywordExtractor
from app.services.matcher import KeywordMatcher
from app.tasks.notification import send_push_notification


class DatabaseTask(Task):
    """Base task with database session handling."""
    _db = None

    def after_return(self, *args, **kwargs):
        """Close database session after task completes."""
        if self._db is not None:
            self._db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.crawler.run_ppomppu_crawler"
)
def run_ppomppu_crawler(self, max_pages: int = 2) -> Dict[str, Any]:
    """
    Run Ppomppu crawler and match deals to users.

    Process:
    1. Crawl Ppomppu (2 pages by default)
    2. For each new deal:
       a. Extract keywords
       b. Find matching users
       c. Send push notifications (async)
    3. Return statistics

    Args:
        max_pages: Number of pages to crawl (default: 2)

    Returns:
        Dictionary with crawling and matching statistics
    """
    db = SessionLocal()
    self._db = db

    try:
        print(f"🕷️  Starting Ppomppu crawler (max_pages={max_pages})...")

        # Initialize crawler
        crawler = PpomppuCrawler(db, include_overseas=False)

        # Run crawler
        stats = crawler.run(max_pages=max_pages)

        # Get newly created deals from this run
        if crawler.crawler_run and stats["new_created"] > 0:
            # Get the new deals
            from app.models.deal import Deal
            from datetime import datetime, timedelta

            # Get deals created in the last 5 minutes (should be from this run)
            cutoff = datetime.utcnow() - timedelta(minutes=5)
            new_deals = db.query(Deal).filter(
                Deal.source_id == crawler.source.id,
                Deal.created_at >= cutoff
            ).all()

            print(f"🔍 Processing {len(new_deals)} new deals for keyword matching...")

            total_matched_users = 0
            total_notifications = 0

            for deal in new_deals:
                # Extract keywords
                keyword_count = KeywordExtractor.extract_and_save(db, deal)
                print(f"   Deal #{deal.id}: {keyword_count} keywords extracted")

                # Refresh deal to get keywords
                db.refresh(deal)

                # Find matching users
                matched_users = KeywordMatcher.match_deal_to_users(db, deal)
                total_matched_users += len(matched_users)

                print(f"   Deal #{deal.id}: Matched {len(matched_users)} users")

                # Send push notifications asynchronously
                for user in matched_users:
                    # Queue notification task
                    send_push_notification.delay(user.id, deal.id)
                    total_notifications += 1

            stats["matched_users"] = total_matched_users
            stats["notifications_queued"] = total_notifications

            print(f"✅ Crawler completed!")
            print(f"   - New deals: {stats['new_created']}")
            print(f"   - Matched users: {total_matched_users}")
            print(f"   - Notifications queued: {total_notifications}")

        else:
            stats["matched_users"] = 0
            stats["notifications_queued"] = 0
            print(f"✅ Crawler completed (no new deals)")

        return {
            "status": "success",
            "stats": stats
        }

    except Exception as e:
        print(f"❌ Crawler task failed: {e}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            return {
                "status": "failed",
                "error": str(e),
                "retries_exceeded": True
            }

    finally:
        db.close()
