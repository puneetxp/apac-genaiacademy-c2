"""add embeddings to supply matching

Revision ID: add_embeddings_supply
Revises: d35ffb77671d
Create Date: 2026-02-23 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'add_embeddings_supply'
down_revision = 'create_marketplace_listings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add embedding fields to supply_requests table
    op.add_column('supply_requests', sa.Column('embedding', Vector(384), nullable=True, comment='Vector embedding for similarity matching (384 dimensions)'))
    op.add_column('supply_requests', sa.Column('embedding_cache_key', sa.String(255), nullable=True, comment='Cache key for embedding to avoid regeneration'))
    
    # Add embedding fields to marketplace_listings table
    op.add_column('marketplace_listings', sa.Column('embedding', Vector(384), nullable=True, comment='Vector embedding for similarity matching (384 dimensions)'))
    op.add_column('marketplace_listings', sa.Column('embedding_cache_key', sa.String(255), nullable=True, comment='Cache key for embedding to avoid regeneration'))
    
    # Create indexes for vector similarity search
    op.execute('CREATE INDEX idx_supply_requests_embedding ON supply_requests USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    op.execute('CREATE INDEX idx_marketplace_listings_embedding ON marketplace_listings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS idx_supply_requests_embedding')
    op.execute('DROP INDEX IF EXISTS idx_marketplace_listings_embedding')
    
    # Drop columns from marketplace_listings
    op.drop_column('marketplace_listings', 'embedding_cache_key')
    op.drop_column('marketplace_listings', 'embedding')
    
    # Drop columns from supply_requests
    op.drop_column('supply_requests', 'embedding_cache_key')
    op.drop_column('supply_requests', 'embedding')
