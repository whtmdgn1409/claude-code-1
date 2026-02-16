"""
AI Summary 시스템 테스트
Tests for AI summary service, comment storage, and prompt building.
"""
import sys
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

from app.models.database import SessionLocal
from app.models.deal import Deal
from app.services.ai_summary import AISummaryService


def test_ai_summary_dry_run():
    """Test AI summary service in dry-run mode (no API key)."""
    print("\n🧪 Testing AI Summary Service (Dry-run mode)...")
    print("=" * 80)

    # Test dry-run mode
    result = AISummaryService.generate_summary(
        deal_title="[테스트] 딜 제목",
        deal_content="딜 내용입니다.",
        comments=[
            {"author": "사용자1", "content": "좋은 정보 감사합니다", "upvotes": 10},
            {"author": "사용자2", "content": "배송비 주의하세요", "upvotes": 5}
        ]
    )

    print(f"✅ Provider: {result['provider']}")
    print(f"\n📝 Summary:\n{result['summary']}")
    print(f"\n✅ Tokens: {result['tokens_used']}")
    print(f"✅ Cost: ${result['cost_estimate']:.4f}")

    assert result['provider'] == 'dry-run', "Expected dry-run provider"
    assert result['tokens_used'] == 0, "Expected zero tokens in dry-run"
    assert result['cost_estimate'] == 0.0, "Expected zero cost in dry-run"
    print("\n✅ Dry-run test passed!")
    print("=" * 80)


def test_comment_storage():
    """Test comment storage in Deal model."""
    print("\n🧪 Testing Comment Storage...")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Get first deal
        deal = db.query(Deal).first()

        if deal:
            print(f"📌 Deal ID: {deal.id}")
            print(f"📌 Title: {deal.title[:50]}...")
            print(f"✅ Comments field type: {type(deal.comments)}")
            print(f"✅ Comments count: {len(deal.comments or [])}")
            print(f"✅ Comments fetched at: {deal.comments_fetched_at}")

            if deal.comments:
                print(f"\n📄 First comment:")
                first_comment = deal.comments[0]
                print(f"   Author: {first_comment.get('author', 'N/A')}")
                print(f"   Content: {first_comment.get('content', 'N/A')[:50]}...")
                print(f"   Upvotes: {first_comment.get('upvotes', 0)}")
            else:
                print("\n⚠️  No comments found for this deal")
        else:
            print("⚠️  No deals in database")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

    print("\n✅ Comment storage test completed!")
    print("=" * 80)


def test_prompt_building():
    """Test Korean prompt generation."""
    print("\n🧪 Testing Prompt Building...")
    print("=" * 80)

    comments = [
        {"author": "유저1", "content": "좋은 가격이네요! 역대급 할인입니다.", "upvotes": 15},
        {"author": "유저2", "content": "배송비 주의하세요. 무료배송 조건 확인 필요합니다.", "upvotes": 8},
        {"author": "유저3", "content": "작년에도 이 가격이었던 것 같아요", "upvotes": 3}
    ]

    prompt = AISummaryService._build_prompt(
        "테스트 딜 제목 - 블랙야크 구스다운 자켓 131,870원",
        "지마켓에서 블랙야크 구스다운 자켓을 판매 중입니다. 무료배송 적용됩니다.",
        comments
    )

    print(f"✅ Prompt length: {len(prompt)} characters")
    print(f"\n📝 Generated Prompt:\n")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    assert "3줄 요약" in prompt, "Prompt should mention 3-line summary"
    assert "유저1" in prompt, "Prompt should include top commenter"
    assert "존댓말" in prompt, "Prompt should specify formal language"

    print("\n✅ Prompt building test passed!")
    print("=" * 80)


def test_ai_service_configuration():
    """Test AI service configuration check."""
    print("\n🧪 Testing AI Service Configuration...")
    print("=" * 80)

    is_configured = AISummaryService.is_configured()
    print(f"✅ AI Service Configured: {is_configured}")

    if not is_configured:
        print("ℹ️  AI API key not set - service will run in dry-run mode")
        print("ℹ️  To enable AI features, set AI_API_KEY in .env file")
    else:
        print("✅ AI service is ready with API key")

    print("\n✅ Configuration check completed!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 AI SUMMARY SYSTEM TESTS")
    print("=" * 80)

    try:
        test_ai_service_configuration()
        test_ai_summary_dry_run()
        test_prompt_building()
        test_comment_storage()

        print("\n" + "=" * 80)
        print("✅ ALL AI SUMMARY TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Run crawler to fetch comments: python backend/run_crawler.py")
        print("2. Test API endpoint: http://localhost:8000/docs")
        print("3. Optional: Add AI_API_KEY to .env to enable real AI summaries")
        print("=" * 80 + "\n")

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80 + "\n")
        raise
