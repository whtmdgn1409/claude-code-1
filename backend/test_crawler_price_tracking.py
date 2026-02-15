"""
크롤러 가격 추적 기능 테스트
Tests price tracking functionality in crawlers
"""
import sys
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

from app.models.database import SessionLocal
from app.models.deal import Deal
from app.models.analytics import PriceHistory
from app.crawlers.ppomppu import PpomppuCrawler


def test_crawler_price_tracking():
    """Test crawler price history collection."""
    db = SessionLocal()

    print("=" * 80)
    print("🧪 Crawler Price Tracking Test")
    print("=" * 80)

    try:
        # Get initial counts
        initial_deals = db.query(Deal).count()
        initial_history = db.query(PriceHistory).count()

        print(f"\n📌 Initial State:")
        print(f"   - Deals: {initial_deals}")
        print(f"   - Price history records: {initial_history}")

        # Run crawler
        print(f"\n🚀 Running Ppomppu crawler...")
        crawler = PpomppuCrawler(db=db)
        stats = crawler.run(max_pages=1)

        print(f"\n✅ Crawler completed:")
        print(f"   - Found: {stats['total_found']}")
        print(f"   - New created: {stats['new_created']}")
        print(f"   - Updated: {stats['updated']}")
        print(f"   - Skipped: {stats['skipped']}")
        print(f"   - Errors: {stats['errors']}")

        # Get final counts
        final_deals = db.query(Deal).count()
        final_history = db.query(PriceHistory).count()

        print(f"\n📌 Final State:")
        print(f"   - Deals: {final_deals} (+{final_deals - initial_deals})")
        print(f"   - Price history records: {final_history} (+{final_history - initial_history})")

        # Check price signals
        deals_with_signals = db.query(Deal).filter(Deal.price_signal != None).count()
        print(f"   - Deals with price signals: {deals_with_signals}")

        # Sample price history
        if final_history > 0:
            print(f"\n📊 Sample Price History:")
            sample_history = db.query(PriceHistory).limit(5).all()
            for ph in sample_history:
                print(f"   - Deal {ph.deal_id}: ₩{ph.price:,} at {ph.recorded_at}")

        # Sample deals with prices
        print(f"\n📊 Sample Deals with Prices:")
        deals_with_prices = db.query(Deal).filter(Deal.price != None).limit(5).all()
        for deal in deals_with_prices:
            signal_emoji = {
                'lowest': '🟢',
                'average': '🟡',
                'high': '🔴',
                None: '⚪'
            }.get(deal.price_signal, '⚪')
            print(f"   {signal_emoji} {deal.title[:40]}... - ₩{deal.price:,} (signal: {deal.price_signal})")

        print("\n" + "=" * 80)
        print("✅ Crawler price tracking test completed!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_crawler_price_tracking()
    sys.exit(0 if success else 1)
