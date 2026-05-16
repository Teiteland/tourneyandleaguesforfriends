"""add game_name to league, tournament, ffa_match, mass_start

Revision ID: 459b95535ba5
Revises: dbbd24d82ab8
Create Date: 2026-05-16 19:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '459b95535ba5'
down_revision = 'dbbd24d82ab8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_name', sa.String(length=100), nullable=True))

    with op.batch_alter_table('tournament', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_name', sa.String(length=100), nullable=True))

    with op.batch_alter_table('ffa_match', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_name', sa.String(length=100), nullable=True))

    with op.batch_alter_table('mass_start', schema=None) as batch_op:
        batch_op.add_column(sa.Column('game_name', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('mass_start', schema=None) as batch_op:
        batch_op.drop_column('game_name')

    with op.batch_alter_table('ffa_match', schema=None) as batch_op:
        batch_op.drop_column('game_name')

    with op.batch_alter_table('tournament', schema=None) as batch_op:
        batch_op.drop_column('game_name')

    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.drop_column('game_name')
