import traceback
from app.core.database import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_clear")

def clear_database():
    """
    Clears all database tables except the users table to maintain login state for E2E tests.
    """
    db = SessionLocal()
    try:
        logger.info("Starting database cleanup (preserving users)...")
        # List all tables
        result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        
        # Exclude tables that should be preserved
        preserve_tables = ["users", "roles", "alembic_version"]
        tables_to_clear = [t for t in tables if t not in preserve_tables]
        
        if not tables_to_clear:
            logger.info("No tables to clear.")
            return

        logger.info(f"Clearing tables: {', '.join(tables_to_clear)}")
        
        # Truncate all tables in a single transaction with CASCADE to handle foreign keys
        truncate_query = text(f"TRUNCATE TABLE {', '.join(tables_to_clear)} CASCADE")
        db.execute(truncate_query)
        db.commit()
        logger.info("Successfully cleared database for testing.")
        
    except Exception as e:
        logger.error(f"Failed to clear database: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    clear_database()
