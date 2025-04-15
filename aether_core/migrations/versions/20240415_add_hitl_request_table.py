"""Add HITL request table

Revision ID: 20240415_add_hitl_request
Revises: 20240414_initial_schema
Create Date: 2024-04-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240415_add_hitl_request'
down_revision = '20240414_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create HITL request table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'hitl_requests'):
        op.create_table(
            'hitl_requests',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id'), nullable=False),
            sa.Column('request_type', sa.String(255), nullable=False),
            sa.Column('request_description', sa.Text, nullable=True),
            sa.Column('options', postgresql.JSON, nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('response', sa.Text, nullable=True),
            sa.Column('response_details', postgresql.JSON, nullable=True),
            sa.Column('human_id', sa.String(255), nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('completed_at', sa.DateTime, nullable=True),
            sa.Column('timeout_seconds', sa.Integer, nullable=True, server_default='3600'),
            sa.Column('urgency', sa.String(50), nullable=True, server_default='normal'),
        )
    
    # Add hitl_requests relationship to tasks table if not already present
    # This is a soft check since we can't directly modify relationships through Alembic
    # The actual relationship is defined in the SQLAlchemy models


def downgrade():
    # Drop HITL request table
    op.drop_table('hitl_requests')