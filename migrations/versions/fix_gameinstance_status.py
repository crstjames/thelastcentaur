"""fix gameinstance status column

Revision ID: fix_gameinstance_status
Revises: 4ae73c4d51eb
Create Date: 2025-02-28 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_gameinstance_status'
down_revision: Union[str, None] = '4ae73c4d51eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Enum type if it doesn't exist
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gamestatus') THEN CREATE TYPE gamestatus AS ENUM ('ACTIVE', 'PAUSED', 'COMPLETED', 'ARCHIVED'); END IF; END $$;")
    
    # Check if status column exists, drop it first if it does (it might be the wrong type)
    op.execute("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gameinstance' AND column_name = 'status') THEN ALTER TABLE gameinstance DROP COLUMN status; END IF; END $$;")
    
    # Add the column with the correct type
    op.add_column('gameinstance', sa.Column('status', sa.Enum('ACTIVE', 'PAUSED', 'COMPLETED', 'ARCHIVED', name='gamestatus'), server_default='ACTIVE', nullable=False))


def downgrade() -> None:
    op.drop_column('gameinstance', 'status') 