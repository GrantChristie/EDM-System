"""empty message

Revision ID: 01d03048ccc2
Revises: 0151d0dc7cb2
Create Date: 2018-03-09 10:56:47.570700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01d03048ccc2'
down_revision = '0151d0dc7cb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_formative_assessments', sa.Column('submitted', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student_formative_assessments', 'submitted')
    # ### end Alembic commands ###
