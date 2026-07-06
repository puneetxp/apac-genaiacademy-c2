"""create ai_usage_quota table

Revision ID: 031
Revises: 030
Create Date: 2026-03-01

Task: AI Usage Quota Management
Validates: Daily GPS-enhanced Bedrock API quota tracking (20 requests/user/day)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '031'
down_revision = 'add_embeddings_supply'
branch_labels = None
depends_on = None


def upgrade():
    """Create ai_usage_quota table"""
    op.create_table(
        'ai_usage_quota',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User ID (references users.id)'),
        sa.Column('date', sa.Date(), nullable=False, comment='Date for quota tracking'),
        sa.Column('gps_enhanced_requests', sa.Integer(), nullable=False, server_default='0', comment='GPS-enhanced Bedrock API calls count'),
        sa.Column('pincode_requests', sa.Integer(), nullable=False, server_default='0', comment='Pincode-based recommendations count'),
        sa.Column('last_reset', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='Last quota reset timestamp'),
        sa.Column('quota_limit', sa.Integer(), nullable=False, server_default='20', comment='Daily GPS-enhanced request limit'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('enable', sa.SmallInteger(), server_default='1', nullable=False),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for common queries
    op.create_index('ix_ai_usage_quota_user_id', 'ai_usage_quota', ['user_id'])
    op.create_index('ix_ai_usage_quota_date', 'ai_usage_quota', ['date'])
    
    # Composite unique index to ensure one record per user per day
    op.create_index(
        'ix_ai_usage_quota_user_date',
        'ai_usage_quota',
        ['user_id', 'date'],
        unique=True
    )


def downgrade():
    """Drop ai_usage_quota table"""
    op.drop_index('ix_ai_usage_quota_user_date', table_name='ai_usage_quota')
    op.drop_index('ix_ai_usage_quota_date', table_name='ai_usage_quota')
    op.drop_index('ix_ai_usage_quota_user_id', table_name='ai_usage_quota')
    op.drop_table('ai_usage_quota')
