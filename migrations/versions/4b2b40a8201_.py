"""add NOT NULL constraint to iso_name column in Language

Revision ID: 4b2b40a8201
Revises: dcf7acac9d
Create Date: 2015-06-22 11:07:45.160782

"""

# revision identifiers, used by Alembic.
revision = '4b2b40a8201'
down_revision = 'dcf7acac9d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('language', 'iso_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('language', 'iso_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    ### end Alembic commands ###