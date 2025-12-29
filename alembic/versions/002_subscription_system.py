"""Subscription system migration

Revision ID: 002
Revises: 001
Create Date: 2024-12-28 21:30:00.000000

Adds subscription plans, payment queue, download history, offer backups,
and updates users and bundles tables with subscription fields.
"""
from alembic import op
import sqlalchemy as sa
import random
import string

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def generate_referral_code():
    """Generate a unique 8-character alphanumeric referral code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def upgrade() -> None:
    # ========================================
    # CREATE NEW TABLES
    # ========================================
    
    # Create subscription_plans table
    op.create_table('subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.String(length=50), nullable=False),
        sa.Column('plan_name', sa.String(length=200), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscription_plans_id'), 'subscription_plans', ['id'], unique=False)
    op.create_index(op.f('ix_subscription_plans_plan_id'), 'subscription_plans', ['plan_id'], unique=True)
    
    # Create payment_queue table
    op.create_table('payment_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('plan_id', sa.String(length=50), nullable=False),
        sa.Column('screenshot_file_id', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('processed_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_queue_id'), 'payment_queue', ['id'], unique=False)
    op.create_index(op.f('ix_payment_queue_user_id'), 'payment_queue', ['user_id'], unique=False)
    
    # Create download_history table
    op.create_table('download_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('bundle_id', sa.Integer(), nullable=False),
        sa.Column('downloaded_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('method', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_download_history_id'), 'download_history', ['id'], unique=False)
    op.create_index(op.f('ix_download_history_user_id'), 'download_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_download_history_bundle_id'), 'download_history', ['bundle_id'], unique=False)
    op.create_index('idx_download_history_user_bundle', 'download_history', ['user_id', 'bundle_id'], unique=False)
    
    # Create offer_backups table
    op.create_table('offer_backups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('offer_name', sa.String(length=100), nullable=False),
        sa.Column('bundle_id', sa.Integer(), nullable=False),
        sa.Column('original_level', sa.String(length=20), nullable=False),
        sa.Column('temporary_level', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offer_backups_id'), 'offer_backups', ['id'], unique=False)
    op.create_index(op.f('ix_offer_backups_bundle_id'), 'offer_backups', ['bundle_id'], unique=False)
    
    # ========================================
    # ALTER EXISTING TABLES
    # ========================================
    
    # Add columns to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('subscription_type', sa.String(length=20), nullable=False, server_default='free'))
        batch_op.add_column(sa.Column('subscription_tier', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('expiry_date', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('referral_tokens', sa.Integer(), nullable=False, server_default='3'))
        batch_op.add_column(sa.Column('referral_code', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('referred_by', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('total_downloads', sa.Integer(), nullable=False, server_default='0'))
    
    # Add index for referral_code (unique)
    op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=True)
    
    # Add access_level column to bundles table
    with op.batch_alter_table('bundles') as batch_op:
        batch_op.add_column(sa.Column('access_level', sa.String(length=20), nullable=False, server_default='free'))
    
    # ========================================
    # SEED INITIAL DATA
    # ========================================
    
    # Insert default subscription plans
    op.execute("""
        INSERT INTO subscription_plans (plan_id, plan_name, duration_days, tier, price, is_active, display_order)
        VALUES 
            ('1m_premium', '1 ماهه پریمیوم', 30, 'premium', 45000, 1, 1),
            ('3m_premium', '3 ماهه پریمیوم', 90, 'premium', 119000, 1, 2),
            ('2m_plus', '2 ماهه پریمیوم پلاس', 60, 'plus', 149000, 1, 3),
            ('4m_plus', '4 ماهه پریمیوم پلاس', 120, 'plus', 270000, 1, 4)
    """)
    
    # Generate referral codes for existing users
    # Note: This is done via raw SQL for SQLite compatibility
    # We'll generate codes in Python and update in batches
    connection = op.get_bind()
    users = connection.execute(sa.text("SELECT id FROM users WHERE referral_code IS NULL")).fetchall()
    
    for user in users:
        code = generate_referral_code()
        # Ensure uniqueness by checking (simple approach, fine for migration)
        while connection.execute(
            sa.text("SELECT 1 FROM users WHERE referral_code = :code"), 
            {"code": code}
        ).fetchone():
            code = generate_referral_code()
        
        connection.execute(
            sa.text("UPDATE users SET referral_code = :code WHERE id = :user_id"),
            {"code": code, "user_id": user[0]}
        )
    
    # Set all existing bundles to premium by default (as per requirements)
    op.execute("UPDATE bundles SET access_level = 'premium' WHERE access_level = 'free'")


def downgrade() -> None:
    # ========================================
    # REMOVE COLUMNS FROM EXISTING TABLES
    # ========================================
    
    # Remove columns from bundles table
    with op.batch_alter_table('bundles') as batch_op:
        batch_op.drop_column('access_level')
    
    # Remove columns from users table
    op.drop_index(op.f('ix_users_referral_code'), table_name='users')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('total_downloads')
        batch_op.drop_column('referred_by')
        batch_op.drop_column('referral_code')
        batch_op.drop_column('referral_tokens')
        batch_op.drop_column('expiry_date')
        batch_op.drop_column('subscription_tier')
        batch_op.drop_column('subscription_type')
    
    # ========================================
    # DROP NEW TABLES
    # ========================================
    
    op.drop_index(op.f('ix_offer_backups_bundle_id'), table_name='offer_backups')
    op.drop_index(op.f('ix_offer_backups_id'), table_name='offer_backups')
    op.drop_table('offer_backups')
    
    op.drop_index('idx_download_history_user_bundle', table_name='download_history')
    op.drop_index(op.f('ix_download_history_bundle_id'), table_name='download_history')
    op.drop_index(op.f('ix_download_history_user_id'), table_name='download_history')
    op.drop_index(op.f('ix_download_history_id'), table_name='download_history')
    op.drop_table('download_history')
    
    op.drop_index(op.f('ix_payment_queue_user_id'), table_name='payment_queue')
    op.drop_index(op.f('ix_payment_queue_id'), table_name='payment_queue')
    op.drop_table('payment_queue')
    
    op.drop_index(op.f('ix_subscription_plans_plan_id'), table_name='subscription_plans')
    op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
    op.drop_table('subscription_plans')
