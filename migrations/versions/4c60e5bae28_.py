"""make priority column for JobStatus

Revision ID: 4c60e5bae28
Revises: 2aa8bd07f9d
Create Date: 2015-07-06 10:42:24.693779

"""

# revision identifiers, used by Alembic.
revision = '4c60e5bae28'
down_revision = '2aa8bd07f9d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_contactinfo_id'), 'contactinfo', ['id'])
    op.create_unique_constraint(op.f('uq_human_id'), 'human', ['id'])
    op.add_column('jobstatus', sa.Column('priority', sa.Integer()))
    op.create_unique_constraint(op.f('uq_jobstatus_id'), 'jobstatus', ['id'])
    op.create_unique_constraint(op.f('uq_jobstatus_priority'), 'jobstatus', ['priority'])
    op.create_unique_constraint(op.f('uq_rating_id'), 'rating', ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_rating_id'), 'rating', type_='unique')
    op.drop_constraint(op.f('uq_jobstatus_priority'), 'jobstatus', type_='unique')
    op.drop_constraint(op.f('uq_jobstatus_id'), 'jobstatus', type_='unique')
    op.drop_column('jobstatus', 'priority')
    op.drop_constraint(op.f('uq_human_id'), 'human', type_='unique')
    op.drop_constraint(op.f('uq_contactinfo_id'), 'contactinfo', type_='unique')
    ### end Alembic commands ###
