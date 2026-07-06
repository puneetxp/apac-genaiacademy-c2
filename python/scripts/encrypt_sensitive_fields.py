"""
Migration script to encrypt sensitive fields in the database
Run this script to encrypt existing sensitive data at rest
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_async_session_maker
from app.core.encryption import get_encryption, SENSITIVE_FIELDS
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def encrypt_table_fields(
    session: AsyncSession,
    table_name: str,
    fields_to_encrypt: list[str]
) -> int:
    """
    Encrypt sensitive fields in a table
    
    Args:
        session: Database session
        table_name: Name of the table
        fields_to_encrypt: List of field names to encrypt
        
    Returns:
        Number of rows updated
    """
    encryption = get_encryption()
    
    # Get all rows from the table
    query = text(f"SELECT id, {', '.join(fields_to_encrypt)} FROM {table_name}")
    result = await session.execute(query)
    rows = result.fetchall()
    
    if not rows:
        logger.info(f"No rows found in {table_name}")
        return 0
    
    updated_count = 0
    
    for row in rows:
        row_id = row[0]
        updates = []
        params = {"row_id": row_id}
        
        for i, field in enumerate(fields_to_encrypt, start=1):
            value = row[i]
            
            if value and isinstance(value, str):
                try:
                    # Encrypt the value
                    encrypted_value = encryption.encrypt_if_not_encrypted(value)
                    updates.append(f"{field} = :field_{i}")
                    params[f"field_{i}"] = encrypted_value
                except Exception as e:
                    logger.error(f"Error encrypting {table_name}.{field} for row {row_id}: {e}")
                    continue
        
        if updates:
            update_query = text(
                f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = :row_id"
            )
            await session.execute(update_query, params)
            updated_count += 1
    
    await session.commit()
    logger.info(f"Encrypted {updated_count} rows in {table_name}")
    
    return updated_count


async def encrypt_users_table(session: AsyncSession) -> int:
    """Encrypt sensitive fields in users table"""
    logger.info("Encrypting users table...")
    
    fields_to_encrypt = []
    
    # Check which fields exist in the table
    result = await session.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'users'"
    ))
    existing_columns = {row[0] for row in result.fetchall()}
    
    # Only encrypt fields that exist
    for field in ['email', 'phone', 'password']:
        if field in existing_columns:
            fields_to_encrypt.append(field)
    
    if not fields_to_encrypt:
        logger.info("No sensitive fields found in users table")
        return 0
    
    return await encrypt_table_fields(session, 'users', fields_to_encrypt)


async def encrypt_marketplace_listings_table(session: AsyncSession) -> int:
    """Encrypt sensitive fields in marketplace_listings table"""
    logger.info("Encrypting marketplace_listings table...")
    
    fields_to_encrypt = []
    
    # Check which fields exist
    result = await session.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'marketplace_listings'"
    ))
    existing_columns = {row[0] for row in result.fetchall()}
    
    # Only encrypt fields that exist
    for field in ['farmer_contact_phone', 'farmer_contact_email']:
        if field in existing_columns:
            fields_to_encrypt.append(field)
    
    if not fields_to_encrypt:
        logger.info("No sensitive fields found in marketplace_listings table")
        return 0
    
    return await encrypt_table_fields(session, 'marketplace_listings', fields_to_encrypt)


async def encrypt_buyer_interests_table(session: AsyncSession) -> int:
    """Encrypt sensitive fields in buyer_interests table"""
    logger.info("Encrypting buyer_interests table...")
    
    fields_to_encrypt = []
    
    # Check which fields exist
    result = await session.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'buyer_interests'"
    ))
    existing_columns = {row[0] for row in result.fetchall()}
    
    # Only encrypt fields that exist
    for field in ['buyer_contact_phone', 'buyer_contact_email']:
        if field in existing_columns:
            fields_to_encrypt.append(field)
    
    if not fields_to_encrypt:
        logger.info("No sensitive fields found in buyer_interests table")
        return 0
    
    return await encrypt_table_fields(session, 'buyer_interests', fields_to_encrypt)


async def main():
    """Main encryption migration"""
    logger.info("=" * 60)
    logger.info("Starting sensitive field encryption migration")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 60)
    
    # Confirm in production
    if settings.ENVIRONMENT == "production":
        response = input("\n⚠️  Running in PRODUCTION. Continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Migration cancelled")
            return
    
    # Create async session
    async_session_maker = get_async_session_maker()
    
    async with async_session_maker() as session:
        try:
            total_updated = 0
            
            # Encrypt users table
            count = await encrypt_users_table(session)
            total_updated += count
            
            # Encrypt marketplace_listings table
            count = await encrypt_marketplace_listings_table(session)
            total_updated += count
            
            # Encrypt buyer_interests table
            count = await encrypt_buyer_interests_table(session)
            total_updated += count
            
            logger.info("=" * 60)
            logger.info(f"✅ Migration completed successfully!")
            logger.info(f"Total rows updated: {total_updated}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
