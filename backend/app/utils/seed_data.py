"""
Database seed data script.
Populates initial data for deal sources, categories, and common blacklist patterns.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.exc import IntegrityError
from app.models.database import SessionLocal, engine, Base
from app.models.deal import DealSource, Category
from app.models.blacklist import Blacklist


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_deal_sources(db):
    """Seed Korean deal sources."""
    print("\nSeeding deal sources...")

    sources = [
        {
            "name": "ppomppu",
            "display_name": "뽐뿌",
            "base_url": "https://www.ppomppu.co.kr",
            "color_code": "#FF6B6B",
            "crawl_interval_minutes": 5,
        },
        {
            "name": "ruliweb",
            "display_name": "루리웹",
            "base_url": "https://bbs.ruliweb.com",
            "color_code": "#4ECDC4",
            "crawl_interval_minutes": 5,
        },
        {
            "name": "fmkorea",
            "display_name": "펨코",
            "base_url": "https://www.fmkorea.com",
            "color_code": "#95E1D3",
            "crawl_interval_minutes": 5,
        },
        {
            "name": "quasarzone",
            "display_name": "퀘이사존",
            "base_url": "https://quasarzone.com",
            "color_code": "#F38181",
            "crawl_interval_minutes": 5,
        },
        {
            "name": "dealbada",
            "display_name": "딜바다",
            "base_url": "https://www.dealbada.com",
            "color_code": "#AA96DA",
            "crawl_interval_minutes": 5,
        },
    ]

    count = 0
    for source_data in sources:
        try:
            source = DealSource(**source_data)
            db.add(source)
            db.commit()
            print(f"  ✓ Added: {source.display_name}")
            count += 1
        except IntegrityError:
            db.rollback()
            print(f"  - Skipped (already exists): {source_data['display_name']}")

    print(f"✓ Seeded {count} deal sources")
    return count


def seed_categories(db):
    """Seed product categories."""
    print("\nSeeding categories...")

    categories = [
        {"name": "전자제품", "slug": "electronics"},
        {"name": "패션/의류", "slug": "fashion"},
        {"name": "식품/음료", "slug": "food"},
        {"name": "뷰티/화장품", "slug": "beauty"},
        {"name": "생활/주방", "slug": "living"},
        {"name": "도서/음반", "slug": "books"},
        {"name": "스포츠/레저", "slug": "sports"},
        {"name": "가구/인테리어", "slug": "furniture"},
        {"name": "디지털/컴퓨터", "slug": "digital"},
        {"name": "유아동", "slug": "baby"},
        {"name": "반려동물", "slug": "pet"},
        {"name": "문화/여행", "slug": "culture"},
        {"name": "자동차/용품", "slug": "automotive"},
        {"name": "게임", "slug": "games"},
        {"name": "기타", "slug": "other"},
    ]

    count = 0
    for cat_data in categories:
        try:
            category = Category(**cat_data)
            db.add(category)
            db.commit()
            print(f"  ✓ Added: {category.name}")
            count += 1
        except IntegrityError:
            db.rollback()
            print(f"  - Skipped (already exists): {cat_data['name']}")

    print(f"✓ Seeded {count} categories")
    return count


def seed_blacklist(db):
    """Seed common blacklist patterns for spam filtering."""
    print("\nSeeding blacklist patterns...")

    patterns = [
        {
            "pattern": "광고",
            "pattern_type": "keyword",
            "target_field": "title",
            "reason": "광고 키워드",
        },
        {
            "pattern": "홍보",
            "pattern_type": "keyword",
            "target_field": "title",
            "reason": "홍보 키워드",
        },
        {
            "pattern": "스팸",
            "pattern_type": "keyword",
            "target_field": "title",
            "reason": "스팸 키워드",
        },
        {
            "pattern": "클릭",
            "pattern_type": "keyword",
            "target_field": "title",
            "reason": "클릭베이트",
        },
    ]

    count = 0
    for bl_data in patterns:
        try:
            blacklist = Blacklist(**bl_data)
            db.add(blacklist)
            db.commit()
            print(f"  ✓ Added: {blacklist.pattern}")
            count += 1
        except IntegrityError:
            db.rollback()
            print(f"  - Skipped (already exists): {bl_data['pattern']}")

    print(f"✓ Seeded {count} blacklist patterns")
    return count


def main():
    """Main seed function."""
    print("=" * 60)
    print("DealMoa Database Seed Script")
    print("=" * 60)

    # Create tables first
    create_tables()

    # Create database session
    db = SessionLocal()

    try:
        # Seed all data
        sources_count = seed_deal_sources(db)
        categories_count = seed_categories(db)
        blacklist_count = seed_blacklist(db)

        print("\n" + "=" * 60)
        print("✓ Seed completed successfully!")
        print(f"  - Deal sources: {sources_count}")
        print(f"  - Categories: {categories_count}")
        print(f"  - Blacklist patterns: {blacklist_count}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
