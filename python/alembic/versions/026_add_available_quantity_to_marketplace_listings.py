"""add available_quantity to marketplace_listings

Revision ID: 026
Revises: 025
Create Date: 2026-03-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '026'
down_revision = '025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add available_quantity column to marketplace_listings table"""
    # Add available_quantity column
    op.add_column('marketplace_listings', 
        sa.Column('available_quantity', sa.Integer(), nullable=True, 
                  comment='Available quantity for booking in kg (defaults to estimated_quantity)')
    )
    
    # Set available_quantity to estimated_quantity for existing records
    op.execute("""
        UPDATE marketplace_listings 
        SET available_quantity = estimated_quantity 
        WHERE available_quantity IS NULL
    """)


def downgrade() -> None:
    """Remove available_quantity column from marketplace_listings table"""
    op.drop_column('marketplace_listings', 'available_quantity')
