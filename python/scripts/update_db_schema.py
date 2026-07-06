"""
Database Schema Update Script
Adds vector columns and indexes to the local PostgreSQL database.
"""

import sys
import os
from sqlalchemy import text

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine

def main():
    print("====================================================")
    print("Database Schema Update: Adding Vector Columns")
    print("====================================================")
    
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # 1. Enable pgvector extension
            print("Verifying pgvector extension is enabled...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # 2. Add rag_embedding column to crop_market_data
            print("Adding 'rag_embedding' column to 'crop_market_data' table...")
            conn.execute(text("""
                ALTER TABLE crop_market_data 
                ADD COLUMN IF NOT EXISTS rag_embedding vector(384)
            """))
            
            # 3. Create HNSW vector index
            print("Creating HNSW index on 'crop_market_data(rag_embedding)'...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_crop_market_data_rag_embedding 
                ON crop_market_data 
                USING hnsw (rag_embedding vector_cosine_ops)
            """))
            
            transaction.commit()
            print("✅ Database schema updated successfully.")
        except Exception as e:
            transaction.rollback()
            print(f"❌ Failed to update database schema: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
