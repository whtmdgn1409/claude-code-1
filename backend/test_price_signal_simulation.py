"""
가격 신호 계산 시뮬레이션 테스트
Price Signal Calculation Simulation Test
"""
import sys
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

from datetime import datetime, timedelta
from app.models.database import SessionLocal
from app.models.deal import Deal
from app.models.analytics import PriceHistory
from app.services.price import PriceService


def test_price_signal_simulation():
    """Test price signal calculation with simulated price history."""
    db = SessionLocal()

    print("=" * 80)
    print("🧪 Price Signal Calculation Simulation Test")
    print("=" * 80)

    try:
        # Get a deal with price
        deal = db.query(Deal).filter(Deal.price != None).first()

        if not deal:
            print("❌ No deals with prices found")
            return False

        print(f"\n📌 Testing with deal:")
        print(f"   ID: {deal.id}")
        print(f"   Title: {deal.title[:60]}...")
        print(f"   Current Price: ₩{deal.price:,}")

        # Simulate price history (create multiple price records)
        print(f"\n🔄 Simulating price history...")

        base_price = deal.price
        simulated_prices = [
            (base_price * 1.2, 30),  # 20% more expensive, 30 days ago
            (base_price * 1.1, 20),  # 10% more expensive, 20 days ago
            (base_price * 1.15, 15), # 15% more expensive, 15 days ago
            (base_price * 1.05, 10), # 5% more expensive, 10 days ago
            (base_price, 5),         # Same price, 5 days ago
            (base_price * 0.95, 2),  # 5% cheaper, 2 days ago (should be lowest)
        ]

        for price, days_ago in simulated_prices:
            price_record = PriceHistory(
                deal_id=deal.id,
                mall_name=deal.mall_name,
                mall_product_id=deal.mall_product_id,
                product_name=deal.product_name,
                price=int(price),
                original_price=deal.original_price,
                discount_rate=deal.discount_rate,
                recorded_at=datetime.utcnow() - timedelta(days=days_ago)
            )
            db.add(price_record)
            print(f"   - ₩{int(price):,} ({days_ago} days ago)")

        db.commit()

        # Get price history count
        history_count = db.query(PriceHistory).filter(
            PriceHistory.deal_id == deal.id
        ).count()
        print(f"\n✅ Created {len(simulated_prices)} simulated price records")
        print(f"   Total history records: {history_count}")

        # Calculate price signal
        print(f"\n🎯 Calculating price signal...")
        signal = PriceService.calculate_price_signal(db, deal)
        print(f"   Signal: {signal}")

        # Get statistics
        stats = PriceService.get_price_statistics(db, deal)
        print(f"\n📊 Price Statistics:")
        print(f"   - Lowest:  ₩{stats['lowest']:,}")
        print(f"   - Highest: ₩{stats['highest']:,}")
        print(f"   - Average: ₩{stats['average']:,}")
        print(f"   - Current: ₩{stats['current']:,}")
        print(f"   - Records: {stats['record_count']}")

        # Update deal price signal
        print(f"\n💾 Updating deal price signal...")
        deal.price_signal = signal
        db.commit()
        print(f"   ✅ Deal price_signal updated to: {signal}")

        # Test different price scenarios
        print(f"\n🧪 Testing different price scenarios:")

        # Scenario 1: Update to lowest price
        deal.price = int(base_price * 0.95)
        signal = PriceService.calculate_price_signal(db, deal)
        signal_emoji = {'lowest': '🟢', 'average': '🟡', 'high': '🔴'}.get(signal, '⚪')
        print(f"   {signal_emoji} Price = ₩{deal.price:,} → Signal: {signal} (should be 'lowest')")

        # Scenario 2: Update to average price
        deal.price = int(base_price * 1.05)
        signal = PriceService.calculate_price_signal(db, deal)
        signal_emoji = {'lowest': '🟢', 'average': '🟡', 'high': '🔴'}.get(signal, '⚪')
        print(f"   {signal_emoji} Price = ₩{deal.price:,} → Signal: {signal} (should be 'average')")

        # Scenario 3: Update to high price
        deal.price = int(base_price * 1.3)
        signal = PriceService.calculate_price_signal(db, deal)
        signal_emoji = {'lowest': '🟢', 'average': '🟡', 'high': '🔴'}.get(signal, '⚪')
        print(f"   {signal_emoji} Price = ₩{deal.price:,} → Signal: {signal} (should be 'high')")

        # Restore original price
        deal.price = base_price
        db.commit()

        print("\n" + "=" * 80)
        print("✅ Price signal simulation test completed successfully!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_price_signal_simulation()
    sys.exit(0 if success else 1)
