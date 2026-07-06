"""
Crop Market Price Embedding Seeder Script
Queries crop_market_data rows lacking embeddings, generates 384-dim embeddings via Vertex AI,
and commits them back to PostgreSQL.
"""

import sys
import os
import time
from sqlalchemy import text

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.services.bedrock_service import BedrockService

def build_embedding_text(row):
    """
    Constructs a rich contextual description string for the embedding model.
    """
    crop_name = row.get("crop_name", "Unknown")
    state = row.get("state", "Unknown")
    district = row.get("district", "Unknown")
    price = row.get("price_per_kg", 0)
    season = row.get("season", "unknown")
    demand = row.get("demand_level", "medium")
    
    return f"crop:{crop_name} state:{state} district:{district} price:{price}/kg season:{season} demand:{demand}"

def seed_embeddings(limit=100):
    print("====================================================")
    print("Crop Market Price Embedding Seeder")
    print("====================================================")
    
    # 1. Initialize Bedrock service
    bedrock = BedrockService()
    if not getattr(bedrock, "vertex_enabled", False):
        print("❌ Vertex AI is not enabled or credentials are not configured.")
        return
        
    # 2. Get rows needing embeddings
    print("Querying PostgreSQL for rows lacking embeddings...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, crop_name, state, district, price_per_kg, season, demand_level 
            FROM crop_market_data 
            WHERE rag_embedding IS NULL 
            LIMIT :limit
        """), {"limit": limit})
        rows = [dict(row._mapping) for row in result]
        
    if not rows:
        print("🎉 All crop market data records already have embeddings!")
        return
        
    print(f"Found {len(rows)} records needing embeddings. Generating vectors in batches...")
    
    success_count = 0
    # Process and update one by one or in small batches
    for idx, row in enumerate(rows):
        text_context = build_embedding_text(row)
        
        # Call Vertex AI embedding generator (configured natively for 384 dimensions)
        vector = bedrock.generate_embedding(text_context, reduce_to_384=True)
        
        if not vector:
            print(f"⚠️ Failed to generate embedding for row ID {row['id']} ({row['crop_name']})")
            continue
            
        # Update row in database
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                conn.execute(text("""
                    UPDATE crop_market_data 
                    SET rag_embedding = :vector 
                    WHERE id = :id
                """), {"vector": vector, "id": row["id"]})
                transaction.commit()
                success_count += 1
            except Exception as e:
                transaction.rollback()
                print(f"❌ Database update failed for row ID {row['id']}: {e}")
                
        if (idx + 1) % 10 == 0 or (idx + 1) == len(rows):
            print(f"Processed {idx + 1}/{len(rows)} records...")
            time.sleep(0.5) # Anti-throttling delay
            
    print(f"\n✅ Completed! Successfully seeded {success_count} embeddings in PostgreSQL.")

if __name__ == "__main__":
    # Default to seeding 20 records for test verification
    limit_val = 20
    if len(sys.argv) > 1:
        try:
            limit_val = int(sys.argv[1])
        except ValueError:
            pass
            
    seed_embeddings(limit=limit_val)
