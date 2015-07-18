"""add ON DELETE CASCADE for JobMatch columns

Revision ID: 3d32478d80f
Revises: 2973449045f
Create Date: 2015-07-15 19:06:41.912857

"""

# revision identifiers, used by Alembic.
revision = '3d32478d80f'
down_revision = '2973449045f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_jobmatch_job_id_job', 'jobmatch', type_='foreignkey')
    op.create_foreign_key('fk_jobmatch_job_id_job', 'jobmatch', 'job', ['job_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_jobmatch_employee_id_employee', 'jobmatch')
    op.create_foreign_key('fk_jobmatch_employee_id_employee', 'jobmatch', 'employee', ['employee_id'], ['id'], ondelete='CASCADE')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_jobmatch_job_id_job', 'jobmatch')
    op.create_foreign_key('fk_jobmatch_job_id_job', 'jobmatch', 'job', ['job_id'], ['id'])
    op.drop_constraint('fk_jobmatch_employee_id_employee', 'jobmatch')
    op.create_foreign_key('fk_jobmatch_employee_id_employee', 'jobmatch', 'employee', ['employee_id'], ['id'])
    ### end Alembic commands ###