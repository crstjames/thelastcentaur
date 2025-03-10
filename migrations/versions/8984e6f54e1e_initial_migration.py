"""Initial migration

Revision ID: 8984e6f54e1e
Revises: 
Create Date: 2025-02-25 19:30:19.208948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8984e6f54e1e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tile',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('position_x', sa.Integer(), nullable=False),
    sa.Column('position_y', sa.Integer(), nullable=False),
    sa.Column('terrain_type', sa.Enum('FOREST', 'CLEARING', 'MOUNTAIN', 'RUINS', 'GRASS', name='terraintype'), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('is_visited', sa.Boolean(), nullable=False),
    sa.Column('items', sa.JSON(), nullable=False),
    sa.Column('enemies', sa.JSON(), nullable=False),
    sa.Column('requirements', sa.JSON(), nullable=False),
    sa.Column('environmental_changes', sa.JSON(), nullable=False),
    sa.Column('exits', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('game_instance_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tile_game_instance_id'), 'tile', ['game_instance_id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('gameinstance',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('current_position', sa.JSON(), nullable=False),
    sa.Column('game_state', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tilehistory',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tile_id', sa.String(length=36), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('event_data', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('game_instance_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['tile_id'], ['tile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tilehistory_game_instance_id'), 'tilehistory', ['game_instance_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tilehistory_game_instance_id'), table_name='tilehistory')
    op.drop_table('tilehistory')
    op.drop_table('gameinstance')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_tile_game_instance_id'), table_name='tile')
    op.drop_table('tile')
    # ### end Alembic commands ###
