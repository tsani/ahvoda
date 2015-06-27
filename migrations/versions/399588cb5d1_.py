"""empty message

Revision ID: 399588cb5d1
Revises: 465d8615449
Create Date: 2015-06-22 17:48:31.976102

"""

# revision identifiers, used by Alembic.
revision = '399588cb5d1'
down_revision = '465d8615449'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job', sa.Column('duration', sa.Float(), nullable=False))
    op.alter_column('job', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('job', 'end_date')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job', sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.alter_column('job', 'start_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('job', 'duration')
    ### end Alembic commands ###