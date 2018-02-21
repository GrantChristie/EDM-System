"""empty message

Revision ID: 6cb99418b891
Revises: 55607abd007b
Create Date: 2018-02-20 14:25:34.609419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cb99418b891'
down_revision = '55607abd007b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('sub_session', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course', 'sub_session')
    # ### end Alembic commands ###