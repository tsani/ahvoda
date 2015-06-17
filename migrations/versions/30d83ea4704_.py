"""link `Business` and `ContactInfo`.

Revision ID: 30d83ea4704
Revises: 163b7cd76a
Create Date: 2015-06-24 21:35:48.083558

"""

# revision identifiers, used by Alembic.
revision = '30d83ea4704'
down_revision = '163b7cd76a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('contact_info_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'business', 'contactinfo', ['contact_info_id'], ['id'])
    op.create_unique_constraint(None, 'contactinfo', ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contactinfo', type_='unique')
    op.drop_constraint(None, 'business', type_='foreignkey')
    op.drop_column('business', 'contact_info_id')
    ### end Alembic commands ###
