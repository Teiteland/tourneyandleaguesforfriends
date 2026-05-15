"""add round_number to ffa_match and mass_start

Revision ID: dbbd24d82ab8
Revises: 744878d56a46
Create Date: 2026-05-15 20:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'dbbd24d82ab8'
down_revision = '744878d56a46'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ffa_match', schema=None) as batch_op:
        batch_op.add_column(sa.Column('round_number', sa.Integer(), nullable=True))

    try:
        with op.batch_alter_table('mass_start', schema=None) as batch_op:
            batch_op.add_column(sa.Column('round_number', sa.Integer(), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('ffa_match', schema=None) as batch_op:
        batch_op.drop_column('round_number')

    try:
        with op.batch_alter_table('mass_start', schema=None) as batch_op:
            batch_op.drop_column('round_number')
    except Exception:
        pass
