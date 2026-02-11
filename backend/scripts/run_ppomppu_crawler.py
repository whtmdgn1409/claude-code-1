"""
Script to run Ppomppu crawler.

Usage:
    python -m scripts.run_ppomppu_crawler
    python -m scripts.run_ppomppu_crawler --pages 10
    python -m scripts.run_ppomppu_crawler --overseas
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.database import SessionLocal
from app.crawlers.ppomppu import run_ppomppu_crawler
from app.services.keyword_extractor import KeywordExtractor
from app.models import Deal


def main():
    """Main entry point for Ppomppu crawler."""
    parser = argparse.ArgumentParser(description="Run Ppomppu (뽐뿌) crawler")
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Number of pages to crawl (default: 5)"
    )
    parser.add_argument(
        "--overseas",
        action="store_true",
        help="Include overseas deals board"
    )
    parser.add_argument(
        "--extract-keywords",
        action="store_true",
        default=True,
        help="Extract keywords from crawled deals (default: True)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Ppomppu (뽐뿌) Crawler")
    print("=" * 60)
    print(f"Pages to crawl: {args.pages}")
    print(f"Include overseas: {args.overseas}")
    print(f"Extract keywords: {args.extract_keywords}")
    print("=" * 60)
    print()

    # Create database session
    db = SessionLocal()

    try:
        # Run crawler
        stats = run_ppomppu_crawler(
            db,
            max_pages=args.pages,
            include_overseas=args.overseas
        )

        print()
        print("=" * 60)
        print("📊 Crawling Results")
        print("=" * 60)
        print(f"Total found: {stats['total_found']}")
        print(f"New deals: {stats['new_created']}")
        print(f"Updated deals: {stats['updated']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 60)

        # Extract keywords if enabled
        if args.extract_keywords and stats['new_created'] > 0:
            print()
            print("🔤 Extracting keywords from new deals...")

            # Get newly created deals (last N deals)
            new_deals = (
                db.query(Deal)
                .filter_by(source_id=1)  # Ppomppu source_id = 1
                .order_by(Deal.created_at.desc())
                .limit(stats['new_created'])
                .all()
            )

            total_keywords = KeywordExtractor.batch_extract_and_save(db, new_deals)

            print(f"✅ Extracted {total_keywords} keywords from {len(new_deals)} deals")
            print(f"   Average: {total_keywords / len(new_deals):.1f} keywords per deal")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

    print()
    print("✅ Crawler completed successfully!")


if __name__ == "__main__":
    main()
