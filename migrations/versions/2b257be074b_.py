"""empty message

Revision ID: 2b257be074b
Revises: 1218fad123
Create Date: 2015-05-15 23:25:54.755642

"""

# revision identifiers, used by Alembic.
revision = '2b257be074b'
down_revision = '1218fad123'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('job', 'create_date', server_default=sa.func.now())
    op.alter_column('position', 'create_date', server_default=sa.func.now())
    op.alter_column('login', 'create_date', server_default=sa.func.now())


def downgrade():
    op.alter_column('job', 'create_date', server_default=None)
    op.alter_column('position', 'create_date', server_default=None)
    op.alter_column('login', 'create_date', server_default=None)
