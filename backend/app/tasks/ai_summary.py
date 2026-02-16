"""
Celery tasks for AI summary generation.
Handles async generation of deal and comment summaries.
"""
from typing import Dict, Any
from datetime import datetime
from celery import Task

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.deal import Deal
from app.services.ai_summary import AISummaryService


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
    name="app.tasks.ai_summary.generate_deal_summary"
)
def generate_deal_summary(self, deal_id: int) -> Dict[str, Any]:
    """
    Generate AI summary for a deal (async background task).

    Process:
    1. Fetch deal from database
    2. Generate summary using AI service (OpenAI/Claude/dry-run)
    3. Save summary to database with timestamp
    4. Return generation metadata

    Args:
        deal_id: ID of the deal to summarize

    Returns:
        Dict with generation status and metadata:
            - deal_id: Deal ID
            - status: "success" or "error"
            - provider: AI provider used
            - tokens_used: Number of tokens consumed
            - cost: Estimated cost in USD
    """
    db = SessionLocal()
    self._db = db

    try:
        # Get deal
        deal = db.query(Deal).filter(Deal.id == deal_id).first()

        if not deal:
            return {
                "status": "error",
                "error": "Deal not found",
                "deal_id": deal_id
            }

        # Generate summary
        result = AISummaryService.generate_summary(
            deal_title=deal.title,
            deal_content=deal.content or "",
            comments=deal.comments or []
        )

        # Save to database
        deal.ai_summary = result['summary']
        deal.ai_summary_generated_at = datetime.utcnow()
        db.commit()

        print(f"✅ Generated AI summary for deal {deal_id} using {result['provider']}")

        return {
            "deal_id": deal_id,
            "status": "success",
            "provider": result['provider'],
            "tokens_used": result['tokens_used'],
            "cost": result['cost_estimate']
        }

    except Exception as e:
        db.rollback()
        print(f"❌ AI summary generation failed for deal {deal_id}: {e}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            return {
                "status": "error",
                "error": str(e),
                "deal_id": deal_id,
                "retries_exceeded": True
            }

    finally:
        db.close()
