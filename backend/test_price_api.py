"""
가격 히스토리 API 테스트
Price History API Test
"""
import sys
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

import requests
from app.models.database import SessionLocal
from app.models.deal import Deal


def test_price_history_api():
    """Test price history API endpoint."""
    db = SessionLocal()

    print("=" * 80)
    print("🧪 Price History API Test")
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
        print(f"   Price: ₩{deal.price:,}")

        # Test API endpoint
        api_url = f"http://localhost:8000/api/v1/deals/{deal.id}/price-history"
        print(f"\n🌐 Calling API: {api_url}")

        try:
            response = requests.get(api_url, params={"days": 30})

            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ API Response (Status: {response.status_code}):")
                print(f"\n📊 Statistics:")
                stats = data.get('statistics', {})
                print(f"   - Lowest Price:  ₩{stats.get('lowest_price', 0):,}" if stats.get('lowest_price') else "   - Lowest Price:  N/A")
                print(f"   - Highest Price: ₩{stats.get('highest_price', 0):,}" if stats.get('highest_price') else "   - Highest Price: N/A")
                print(f"   - Average Price: ₩{stats.get('average_price', 0):,}" if stats.get('average_price') else "   - Average Price: N/A")
                print(f"   - Current Price: ₩{stats.get('current_price', 0):,}" if stats.get('current_price') else "   - Current Price: N/A")
                print(f"   - Record Count:  {stats.get('record_count', 0)}")
                print(f"   - Price Signal:  {stats.get('price_signal', 'None')}")

                print(f"\n📝 Price History Records:")
                history = data.get('history', [])
                if history:
                    for record in history[:5]:  # Show first 5
                        print(f"   - ₩{record['price']:,} at {record['recorded_at'][:19]}")
                    if len(history) > 5:
                        print(f"   ... and {len(history) - 5} more records")
                else:
                    print("   No history records")

                print("\n✅ API test passed!")
                return True

            else:
                print(f"❌ API returned status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API server")
            print("   Please start the server with: uvicorn app.main:app --reload")
            return False

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_price_history_api()
    print("\n" + "=" * 80)
    if success:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Make sure the API server is running.")
    print("=" * 80)
    sys.exit(0 if success else 1)
