"""add `State` and `ContactInfo`; link `Job` to `Business`

Revision ID: 163b7cd76a
Revises: 2e1051f634f
Create Date: 2015-06-24 21:22:36.605715

"""

# revision identifiers, used by Alembic.
revision = '163b7cd76a'
down_revision = '2e1051f634f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contactinfo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('email_address', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('state',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['country.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('city', sa.Column('state_id', sa.Integer(), nullable=False))
    op.create_foreign_key('city_state_id_fkey', 'city', 'state', ['state_id'], ['id'])
    op.add_column('human', sa.Column('contact_info_id', sa.Integer(), nullable=False))
    op.create_foreign_key('human_contact_info_id_fkey', 'human', 'contactinfo', ['contact_info_id'], ['id'])
    op.add_column('job', sa.Column('business_id', sa.Integer(), nullable=False))
    op.alter_column('job', 'rating_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key('job_business_id_fkey', 'job', 'business', ['business_id'], ['id'])
    op.add_column('location', sa.Column('postal_code', sa.String(), nullable=False))
    op.drop_constraint('location_country_id_fkey', 'location', type_='foreignkey')
    op.drop_column('location', 'country_id')
    op.drop_column('login', 'phone_number')
    op.drop_column('login', 'postal_code')
    op.drop_column('login', 'email')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('login', sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('login', sa.Column('postal_code', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('login', sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('location', sa.Column('country_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('location_country_id_fkey', 'location', 'country', ['country_id'], ['id'])
    op.drop_column('location', 'postal_code')
    op.drop_constraint('job_business_id_fkey', 'job', type_='foreignkey')
    op.alter_column('job', 'rating_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('job', 'business_id')
    op.drop_constraint('human_contact_info_id_fkey', 'human', type_='foreignkey')
    op.drop_column('human', 'contact_info_id')
    op.drop_constraint('city_state_id_fkey', 'city', type_='foreignkey')
    op.drop_column('city', 'state_id')
    op.drop_table('state')
    op.drop_table('contactinfo')
    ### end Alembic commands ###
