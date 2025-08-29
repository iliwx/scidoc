"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_user_id', sa.BigInteger(), nullable=False),
    sa.Column('first_seen', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_tg_user_id'), 'users', ['tg_user_id'], unique=True)
    
    # Create mandatory_channels table
    op.create_table('mandatory_channels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('join_link', sa.String(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mandatory_channels_chat_id'), 'mandatory_channels', ['chat_id'], unique=False)
    op.create_index(op.f('ix_mandatory_channels_id'), 'mandatory_channels', ['id'], unique=False)
    
    # Create bundles table
    op.create_table('bundles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_number', sa.Integer(), nullable=False),
    sa.Column('public_number_str', sa.String(length=10), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('created_by', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bundles_code'), 'bundles', ['code'], unique=True)
    op.create_index(op.f('ix_bundles_id'), 'bundles', ['id'], unique=False)
    op.create_index(op.f('ix_bundles_public_number'), 'bundles', ['public_number'], unique=True)
    op.create_index(op.f('ix_bundles_public_number_str'), 'bundles', ['public_number_str'], unique=False)
    
    # Create bundle_items table
    op.create_table('bundle_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bundle_id', sa.Integer(), nullable=False),
    sa.Column('from_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('media_type', sa.String(length=50), nullable=True),
    sa.Column('caption_json', sa.JSON(), nullable=True),
    sa.Column('extra_json', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['bundle_id'], ['bundles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bundle_items_bundle_id'), 'bundle_items', ['bundle_id'], unique=False)
    op.create_index(op.f('ix_bundle_items_id'), 'bundle_items', ['id'], unique=False)
    
    # Create deliveries table
    op.create_table('deliveries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bundle_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('delivered_at', sa.DateTime(), nullable=False),
    sa.Column('messages_json', sa.JSON(), nullable=False),
    sa.Column('delete_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deliveries_bundle_id'), 'deliveries', ['bundle_id'], unique=False)
    op.create_index(op.f('ix_deliveries_delete_at'), 'deliveries', ['delete_at'], unique=False)
    op.create_index(op.f('ix_deliveries_id'), 'deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_deliveries_user_id'), 'deliveries', ['user_id'], unique=False)
    op.create_index('idx_delivery_delete_at', 'deliveries', ['delete_at'], unique=False)
    
    # Create starting_messages table
    op.create_table('starting_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_chat_id', sa.BigInteger(), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create ending_messages table
    op.create_table('ending_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('from_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ending_messages_id'), 'ending_messages', ['id'], unique=False)
    op.create_index(op.f('ix_ending_messages_name'), 'ending_messages', ['name'], unique=True)
    
    # Create ending_rotations table
    op.create_table('ending_rotations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('ending_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ending_rotations_id'), 'ending_rotations', ['id'], unique=False)
    op.create_index(op.f('ix_ending_rotations_user_id'), 'ending_rotations', ['user_id'], unique=False)
    op.create_index('idx_ending_rotation_user_date', 'ending_rotations', ['user_id', 'date'], unique=False)
    
    # Create requests table
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_id'), 'requests', ['id'], unique=False)
    op.create_index(op.f('ix_requests_user_id'), 'requests', ['user_id'], unique=False)
    
    # Create settings table
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('next_public_number', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Insert initial settings
    op.execute("INSERT INTO settings (id, next_public_number) VALUES (1, 1)")


def downgrade() -> None:
    op.drop_table('settings')
    op.drop_index('idx_ending_rotation_user_date', table_name='ending_rotations')
    op.drop_index(op.f('ix_ending_rotations_user_id'), table_name='ending_rotations')
    op.drop_index(op.f('ix_ending_rotations_id'), table_name='ending_rotations')
    op.drop_table('ending_rotations')
    op.drop_index(op.f('ix_ending_messages_name'), table_name='ending_messages')
    op.drop_index(op.f('ix_ending_messages_id'), table_name='ending_messages')
    op.drop_table('ending_messages')
    op.drop_table('starting_messages')
    op.drop_index('idx_delivery_delete_at', table_name='deliveries')
    op.drop_index(op.f('ix_deliveries_user_id'), table_name='deliveries')
    op.drop_index(op.f('ix_deliveries_id'), table_name='deliveries')
    op.drop_index(op.f('ix_deliveries_delete_at'), table_name='deliveries')
    op.drop_index(op.f('ix_deliveries_bundle_id'), table_name='deliveries')
    op.drop_table('deliveries')
    op.drop_index(op.f('ix_bundle_items_id'), table_name='bundle_items')
    op.drop_index(op.f('ix_bundle_items_bundle_id'), table_name='bundle_items')
    op.drop_table('bundle_items')
    op.drop_index(op.f('ix_bundles_public_number_str'), table_name='bundles')
    op.drop_index(op.f('ix_bundles_public_number'), table_name='bundles')
    op.drop_index(op.f('ix_bundles_id'), table_name='bundles')
    op.drop_index(op.f('ix_bundles_code'), table_name='bundles')
    op.drop_table('bundles')
    op.drop_index(op.f('ix_mandatory_channels_id'), table_name='mandatory_channels')
    op.drop_index(op.f('ix_mandatory_channels_chat_id'), table_name='mandatory_channels')
    op.drop_table('mandatory_channels')
    op.drop_index(op.f('ix_users_tg_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
