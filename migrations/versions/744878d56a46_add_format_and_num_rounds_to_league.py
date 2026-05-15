"""add format and num_rounds to league

Revision ID: 744878d56a46
Revises: 8b046cd5d45d
Create Date: 2026-05-15 21:36:34.318603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '744878d56a46'
down_revision = '8b046cd5d45d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.add_column(sa.Column('format', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('num_rounds', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.drop_column('num_rounds')
        batch_op.drop_column('format')
