"""
가격 추적 시스템 End-to-End 테스트
Price Tracking System Integration Test
"""
import sys
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

from app.models.database import SessionLocal
from app.models.deal import Deal
from app.models.analytics import PriceHistory
from app.services.price import PriceService


def test_price_tracking():
    """Test price tracking system integration."""
    db = SessionLocal()

    print("=" * 80)
    print("🧪 Price Tracking System Integration Test")
    print("=" * 80)

    try:
        # 1. Test deal retrieval
        print("\n📌 Step 1: Retrieving test deals...")
        deals = db.query(Deal).filter(
            Deal.deleted_at == None,
            Deal.price != None
        ).limit(10).all()

        if not deals:
            print("❌ No deals found in database")
            return False

        print(f"✅ Found {len(deals)} deals with prices")

        # 2. Price history verification
        print("\n📌 Step 2: Checking price history records...")
        total_history = 0
        deals_with_history = 0

        for deal in deals:
            history_count = db.query(PriceHistory).filter(
                PriceHistory.deal_id == deal.id
            ).count()

            if history_count > 0:
                deals_with_history += 1
                total_history += history_count

        print(f"✅ Total price history records: {total_history}")
        print(f"✅ Deals with history: {deals_with_history}/{len(deals)}")

        # 3. Price signal distribution
        print("\n📌 Step 3: Analyzing price signal distribution...")
        signal_counts = {
            'lowest': 0,
            'average': 0,
            'high': 0,
            None: 0
        }

        for deal in deals:
            signal = deal.price_signal
            if signal in signal_counts:
                signal_counts[signal] += 1
            else:
                signal_counts[None] += 1

        print(f"🟢 LOWEST:  {signal_counts['lowest']} deals")
        print(f"🟡 AVERAGE: {signal_counts['average']} deals")
        print(f"🔴 HIGH:    {signal_counts['high']} deals")
        print(f"⚪ None:    {signal_counts[None]} deals (insufficient history)")

        # 4. Test price signal calculation
        print("\n📌 Step 4: Testing price signal calculation...")
        test_deal = deals[0]
        print(f"Testing with deal: {test_deal.title[:50]}... (ID={test_deal.id})")

        signal = PriceService.calculate_price_signal(db, test_deal)
        print(f"✅ Calculated signal: {signal}")

        # 5. Test statistics calculation
        print("\n📌 Step 5: Testing price statistics...")
        stats = PriceService.get_price_statistics(db, test_deal)
        print(f"✅ Statistics:")
        print(f"   - Lowest:  ₩{stats['lowest']:,}" if stats['lowest'] else "   - Lowest:  N/A")
        print(f"   - Highest: ₩{stats['highest']:,}" if stats['highest'] else "   - Highest: N/A")
        print(f"   - Average: ₩{stats['average']:,}" if stats['average'] else "   - Average: N/A")
        print(f"   - Current: ₩{stats['current']:,}" if stats['current'] else "   - Current: N/A")
        print(f"   - Records: {stats['record_count']}")

        # 6. Summary
        print("\n" + "=" * 80)
        print("📊 Test Summary")
        print("=" * 80)
        print(f"✅ Total deals tested: {len(deals)}")
        print(f"✅ Deals with price history: {deals_with_history}")
        print(f"✅ Total price history records: {total_history}")
        print(f"✅ Price signal distribution:")
        print(f"   - 🟢 LOWEST:  {signal_counts['lowest']}")
        print(f"   - 🟡 AVERAGE: {signal_counts['average']}")
        print(f"   - 🔴 HIGH:    {signal_counts['high']}")
        print(f"   - ⚪ None:    {signal_counts[None]}")
        print("\n✅ Price tracking system integration test completed successfully!")
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
    success = test_price_tracking()
    sys.exit(0 if success else 1)
