"""add possibility for default settings in Position table

Specifically, each position defines a default pay, default description, and
default set of required languages. These will pre-fill the listing creation
form.

Revision ID: 49ae29b543
Revises: 1b1f4b2ebf6
Create Date: 2015-07-09 06:13:26.969112

"""

# revision identifiers, used by Alembic.
revision = '49ae29b543'
down_revision = '1b1f4b2ebf6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('positionlanguageset',
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.Column('position_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], name=op.f('fk_positionlanguageset_language_id_language'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['position_id'], ['position.id'], name=op.f('fk_positionlanguageset_position_id_position'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('language_id', 'position_id', name=op.f('pk_positionlanguageset'))
    )
    op.add_column('position', sa.Column('default_details', sa.String(), nullable=True))
    op.add_column('position', sa.Column('default_pay', sa.Float(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('position', 'default_pay')
    op.drop_column('position', 'default_details')
    op.drop_table('positionlanguageset')
    ### end Alembic commands ###
