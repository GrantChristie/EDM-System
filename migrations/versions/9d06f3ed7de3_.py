"""empty message

Revision ID: 9d06f3ed7de3
Revises: d53873408855
Create Date: 2018-03-13 09:26:38.735276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d06f3ed7de3'
down_revision = 'd53873408855'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_summative_assessments', sa.Column('submitted', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student_summative_assessments', 'submitted')
    # ### end Alembic commands ###