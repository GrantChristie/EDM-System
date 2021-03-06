"""empty message

Revision ID: 0151d0dc7cb2
Revises: 4ae441195f51
Create Date: 2018-03-09 10:55:49.372139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0151d0dc7cb2'
down_revision = '4ae441195f51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student_formative_assessments', 'submitted')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_formative_assessments', sa.Column('submitted', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
