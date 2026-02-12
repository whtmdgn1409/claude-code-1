"""
Quick test script for MVP features.
Tests bookmark and matched deals APIs.
"""
import sys
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, '/Users/choseunghu/Desktop/claude-code-1/backend')

from app.models.database import SessionLocal
from app.models.user import User, UserKeyword
from app.models.deal import Deal
from app.services.bookmark import BookmarkService
from app.services.matcher import KeywordMatcher
from app.services.keyword_extractor import KeywordExtractor


def test_bookmark_service():
    """Test bookmark service functionality."""
    print("\n🧪 Testing Bookmark Service...")
    db: Session = SessionLocal()

    try:
        # Get first user and deal
        user = db.query(User).first()
        deal = db.query(Deal).first()

        if not user or not deal:
            print("   ⚠️  Need user and deal to test bookmarks")
            return

        print(f"   User: {user.email}")
        print(f"   Deal: {deal.title[:50]}...")

        # Test add bookmark
        try:
            bookmark = BookmarkService.add_bookmark(
                db=db,
                user_id=user.id,
                deal_id=deal.id,
                notes="Test bookmark"
            )
            print(f"   ✅ Bookmark created: ID={bookmark.id}")

            # Test check is_bookmarked
            is_bookmarked = BookmarkService.check_is_bookmarked(
                db=db,
                user_id=user.id,
                deal_id=deal.id
            )
            print(f"   ✅ Is bookmarked: {is_bookmarked}")

            # Test get bookmarks
            result = BookmarkService.get_user_bookmarks(db=db, user_id=user.id)
            print(f"   ✅ User bookmarks: {result['total']} total")

            # Test delete
            BookmarkService.delete_bookmark(
                db=db,
                bookmark_id=bookmark.id,
                user_id=user.id
            )
            print(f"   ✅ Bookmark deleted")

        except ValueError as e:
            print(f"   ⚠️  Error: {e}")

    finally:
        db.close()


def test_keyword_matcher():
    """Test keyword matching functionality."""
    print("\n🧪 Testing Keyword Matcher...")
    db: Session = SessionLocal()

    try:
        # Get first user with keywords
        user = db.query(User).join(UserKeyword).first()

        if not user:
            print("   ⚠️  Need user with keywords to test matching")
            return

        print(f"   User: {user.email}")

        # Get user keywords
        keywords = db.query(UserKeyword).filter(
            UserKeyword.user_id == user.id,
            UserKeyword.is_active == True
        ).all()

        print(f"   User has {len(keywords)} keywords:")
        for kw in keywords[:5]:
            prefix = "+" if kw.is_inclusion else "-"
            print(f"      {prefix} {kw.keyword}")

        # Test match_user_to_deals
        result = KeywordMatcher.match_user_to_deals(
            db=db,
            user=user,
            page=1,
            page_size=10,
            days=30
        )

        print(f"   ✅ Matched deals: {result['total']} total")
        if result['deals']:
            print(f"   Top matched deals:")
            for deal in result['deals'][:3]:
                print(f"      - {deal.title[:60]}...")

    finally:
        db.close()


def test_keyword_extractor():
    """Test keyword extraction."""
    print("\n🧪 Testing Keyword Extractor...")
    db: Session = SessionLocal()

    try:
        # Get a deal
        deal = db.query(Deal).first()

        if not deal:
            print("   ⚠️  Need deal to test keyword extraction")
            return

        print(f"   Deal: {deal.title[:60]}...")

        # Extract keywords
        count = KeywordExtractor.extract_and_save(db, deal)
        print(f"   ✅ Extracted {count} keywords")

        # Show keywords
        from app.models.analytics import DealKeyword
        keywords = db.query(DealKeyword).filter(
            DealKeyword.deal_id == deal.id
        ).limit(10).all()

        if keywords:
            print(f"   Keywords:")
            for kw in keywords:
                print(f"      - {kw.keyword} ({kw.source})")

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DealMoa MVP Test Suite")
    print("=" * 60)

    test_bookmark_service()
    test_keyword_matcher()
    test_keyword_extractor()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
