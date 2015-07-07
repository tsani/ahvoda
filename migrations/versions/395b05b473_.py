"""add NOT NULL constraint to priority column of JobStatus

Revision ID: 395b05b473
Revises: 4c60e5bae28
Create Date: 2015-07-06 10:59:26.352935

"""

# revision identifiers, used by Alembic.
revision = '395b05b473'
down_revision = '4c60e5bae28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobstatus', 'priority',
               existing_type=sa.INTEGER(),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobstatus', 'priority',
               existing_type=sa.INTEGER(),
               nullable=True)
    ### end Alembic commands ###