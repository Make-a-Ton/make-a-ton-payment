"""team

Revision ID: d5ab3378491f
Revises: 0e0448786908
Create Date: 2022-09-24 22:34:36.730961

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'd5ab3378491f'
down_revision = '0e0448786908'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team', sa.Column('members', sa.ARRAY(sa.Integer()), nullable=True))
    op.alter_column('team', 'lead',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('team_lead_fkey', 'team', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('team_lead_fkey', 'team', 'user', ['lead'], ['id'])
    op.alter_column('team', 'lead',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('team', 'members')
    # ### end Alembic commands ###
