"""add applicants table

Revision ID: 41bf2d965d2
Revises: 3ee911eb470
Create Date: 2015-06-26 04:13:05.265487

"""

# revision identifiers, used by Alembic.
revision = '41bf2d965d2'
down_revision = '3ee911eb470'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('applicant',
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('employee_id', 'job_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('applicant')
    ### end Alembic commands ###