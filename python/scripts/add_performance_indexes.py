"""
Add Performance Indexes
Creates database indexes for common query patterns to improve performance
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import settings
from app.core.query_optimizer import QueryOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_indexes():
    """Add performance indexes to database"""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )
    
    # Create session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            logger.info("Starting index creation...")
            
            # Get common indexes
            indexes = QueryOptimizer.get_common_indexes()
            
            logger.info(f"Creating {len(indexes)} indexes...")
            
            # Create each index
            for index_def in indexes:
                try:
                    name = index_def["name"]
                    table = index_def["table"]
                    columns = index_def["columns"]
                    unique = index_def.get("unique", False)
                    
                    # Build CREATE INDEX statement
                    unique_str = "UNIQUE " if unique else ""
                    columns_str = ", ".join(columns)
                    
                    sql = f"""
                    CREATE INDEX IF NOT EXISTS {name}
                    ON {table} ({columns_str})
                    """
                    
                    await session.execute(text(sql))
                    await session.commit()
                    
                    logger.info(f"✓ Created index {name} on {table}({columns_str})")
                    
                except Exception as e:
                    logger.error(f"✗ Error creating index {index_def.get('name')}: {e}")
                    await session.rollback()
            
            logger.info("Index creation completed!")
            
        except Exception as e:
            logger.error(f"Error in index creation: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_indexes())
