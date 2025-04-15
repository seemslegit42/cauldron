"""Add HITL tables

Revision ID: 20240517_add_hitl_tables
Revises: 
Create Date: 2024-05-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240517_add_hitl_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create HITLRequest table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'hitl_requests'):
        op.create_table(
            'hitl_requests',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id'), nullable=False),
            sa.Column('request_type', sa.String(255), nullable=False),
            sa.Column('request_description', sa.Text(), nullable=True),
            sa.Column('options', postgresql.JSON(), nullable=True),
            sa.Column('status', sa.String(50), nullable=False, default='pending'),
            sa.Column('response', sa.Text(), nullable=True),
            sa.Column('response_details', postgresql.JSON(), nullable=True),
            sa.Column('human_id', sa.String(255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
        )
    
    # Add subtasks column to tasks table if it doesn't exist
    op.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='subtasks'")
    result = op.get_bind().fetchone()
    if not result:
        op.add_column('tasks', sa.Column('subtasks', postgresql.JSON(), nullable=True, server_default='[]'))
    
    # Add hitl_requests_json column to tasks table if it doesn't exist
    op.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='hitl_requests_json'")
    result = op.get_bind().fetchone()
    if not result:
        op.add_column('tasks', sa.Column('hitl_requests_json', postgresql.JSON(), nullable=True, server_default='[]'))


def downgrade():
    # Drop hitl_requests_json column from tasks table
    op.drop_column('tasks', 'hitl_requests_json')
    
    # Drop subtasks column from tasks table
    op.drop_column('tasks', 'subtasks')
    
    # Drop HITLRequest table
    op.drop_table('hitl_requests')