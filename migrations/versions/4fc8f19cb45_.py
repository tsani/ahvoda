"""add column to Manager account describing whether they've accepted the ToS

Revision ID: 4fc8f19cb45
Revises: 395b05b473
Create Date: 2015-07-07 16:08:29.822759

"""

# revision identifiers, used by Alembic.
revision = '4fc8f19cb45'
down_revision = '395b05b473'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('manager', sa.Column('is_tos_approved', sa.Boolean(), server_default='f', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('manager', 'is_tos_approved')
    ### end Alembic commands ###
