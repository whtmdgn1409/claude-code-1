"""
Additional database indexes and extensions setup.
Creates PostgreSQL-specific indexes and enables extensions.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import text
from app.models.database import engine


def create_extensions():
    """Create PostgreSQL extensions required for the application."""
    print("Creating PostgreSQL extensions...")

    with engine.connect() as conn:
        # Create pg_trgm extension for Korean text search
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        conn.commit()
        print("  ✓ Created extension: pg_trgm (for Korean text search)")


def create_custom_indexes():
    """
    Create additional custom indexes not defined in models.
    These are performance-critical indexes for specific query patterns.
    """
    print("\nCreating custom indexes...")

    indexes = [
        # Additional composite index for feed queries with category filter
        """
        CREATE INDEX IF NOT EXISTS idx_deals_category_feed
        ON deals(category_id, is_active, published_at DESC, hot_score DESC)
        WHERE deleted_at IS NULL AND is_blocked = false;
        """,

        # Index for price history aggregation queries
        """
        CREATE INDEX IF NOT EXISTS idx_price_history_product_agg
        ON price_history(mall_product_id, price, recorded_at)
        WHERE mall_product_id IS NOT NULL;
        """,

        # Index for notification delivery tracking
        """
        CREATE INDEX IF NOT EXISTS idx_notifications_pending
        ON notifications(status, created_at)
        WHERE status = 'PENDING';
        """,

        # Index for user active keywords lookup
        """
        CREATE INDEX IF NOT EXISTS idx_user_keywords_lookup
        ON user_keywords(user_id, keyword, is_inclusion)
        WHERE is_active = true;
        """,
    ]

    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql))
                conn.commit()
                # Extract index name from SQL for logging
                idx_name = idx_sql.split("idx_")[1].split("\n")[0].strip()
                print(f"  ✓ Created index: idx_{idx_name}")
            except Exception as e:
                print(f"  - Error creating index: {e}")


def create_triggers():
    """
    Create database triggers for automatic updates.
    """
    print("\nCreating database triggers...")

    # Trigger to auto-update updated_at timestamp
    trigger_sql = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """

    with engine.connect() as conn:
        try:
            conn.execute(text(trigger_sql))
            conn.commit()
            print("  ✓ Created function: update_updated_at_column()")
        except Exception as e:
            print(f"  - Error creating trigger function: {e}")

    # Apply trigger to all tables with updated_at column
    tables_with_updated_at = [
        "deal_sources", "categories", "deals", "users", "user_keywords",
        "user_devices", "bookmarks", "notifications", "price_history",
        "deal_statistics", "deal_keywords", "crawler_runs", "crawler_errors",
        "crawler_state", "blacklist"
    ]

    with engine.connect() as conn:
        for table in tables_with_updated_at:
            trigger_name = f"trigger_update_{table}_updated_at"
            trigger_sql = f"""
            DROP TRIGGER IF EXISTS {trigger_name} ON {table};
            CREATE TRIGGER {trigger_name}
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            """
            try:
                conn.execute(text(trigger_sql))
                conn.commit()
                print(f"  ✓ Created trigger: {trigger_name}")
            except Exception as e:
                print(f"  - Error creating trigger for {table}: {e}")


def main():
    """Main function to set up all indexes and extensions."""
    print("=" * 60)
    print("DealMoa Database Indexes & Extensions Setup")
    print("=" * 60)

    try:
        create_extensions()
        create_custom_indexes()
        create_triggers()

        print("\n" + "=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        raise


if __name__ == "__main__":
    main()
