"""
Celery tasks for automated crawling.
Runs crawlers periodically and triggers keyword matching.
"""
from typing import Dict, Any
from celery import Task

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.crawlers.ppomppu import PpomppuCrawler
from app.crawlers.ruliweb import RuliwebCrawler
from app.crawlers.quasarzone import QuasarzoneCrawler
from app.crawlers.fmkorea import FmkoreaCrawler
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


def _run_crawler_task(task, crawler, db, max_pages: int) -> Dict[str, Any]:
    """
    Common crawler execution logic.
    Runs the crawler, extracts keywords, matches users, and queues notifications.
    """
    source_name = crawler.source_name

    try:
        print(f"🕷️  Starting {source_name} crawler (max_pages={max_pages})...")

        # Run crawler
        stats = crawler.run(max_pages=max_pages)

        # Get newly created deals from this run
        if crawler.crawler_run and stats["new_created"] > 0:
            from app.models.deal import Deal
            from datetime import datetime, timedelta

            cutoff = datetime.utcnow() - timedelta(minutes=5)
            new_deals = db.query(Deal).filter(
                Deal.source_id == crawler.source.id,
                Deal.created_at >= cutoff
            ).all()

            print(f"🔍 Processing {len(new_deals)} new deals for keyword matching...")

            total_matched_users = 0
            total_notifications = 0

            for deal in new_deals:
                keyword_count = KeywordExtractor.extract_and_save(db, deal)
                print(f"   Deal #{deal.id}: {keyword_count} keywords extracted")

                db.refresh(deal)

                matched_users = KeywordMatcher.match_deal_to_users(db, deal)
                total_matched_users += len(matched_users)

                print(f"   Deal #{deal.id}: Matched {len(matched_users)} users")

                for user in matched_users:
                    send_push_notification.delay(user.id, deal.id)
                    total_notifications += 1

            stats["matched_users"] = total_matched_users
            stats["notifications_queued"] = total_notifications

            print(f"✅ {source_name} crawler completed!")
            print(f"   - New deals: {stats['new_created']}")
            print(f"   - Matched users: {total_matched_users}")
            print(f"   - Notifications queued: {total_notifications}")

        else:
            stats["matched_users"] = 0
            stats["notifications_queued"] = 0
            print(f"✅ {source_name} crawler completed (no new deals)")

        return {"status": "success", "source": source_name, "stats": stats}

    except Exception as e:
        print(f"❌ {source_name} crawler task failed: {e}")

        try:
            raise task.retry(exc=e, countdown=60 * (task.request.retries + 1))
        except task.MaxRetriesExceededError:
            return {
                "status": "failed",
                "source": source_name,
                "error": str(e),
                "retries_exceeded": True
            }

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.crawler.run_ppomppu_crawler"
)
def run_ppomppu_crawler(self, max_pages: int = 2) -> Dict[str, Any]:
    """Run Ppomppu crawler and match deals to users."""
    db = SessionLocal()
    self._db = db
    crawler = PpomppuCrawler(db, include_overseas=False)
    return _run_crawler_task(self, crawler, db, max_pages)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.crawler.run_ruliweb_crawler"
)
def run_ruliweb_crawler(self, max_pages: int = 2) -> Dict[str, Any]:
    """Run Ruliweb crawler and match deals to users."""
    db = SessionLocal()
    self._db = db
    crawler = RuliwebCrawler(db)
    return _run_crawler_task(self, crawler, db, max_pages)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.crawler.run_quasarzone_crawler"
)
def run_quasarzone_crawler(self, max_pages: int = 2) -> Dict[str, Any]:
    """Run Quasarzone crawler and match deals to users."""
    db = SessionLocal()
    self._db = db
    crawler = QuasarzoneCrawler(db)
    return _run_crawler_task(self, crawler, db, max_pages)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.crawler.run_fmkorea_crawler"
)
def run_fmkorea_crawler(self, max_pages: int = 2) -> Dict[str, Any]:
    """Run FMKorea crawler and match deals to users."""
    db = SessionLocal()
    self._db = db
    crawler = FmkoreaCrawler(db)
    return _run_crawler_task(self, crawler, db, max_pages)
