"""empty message

Revision ID: 89c1b43b8dd0
Revises: 2835da95262c
Create Date: 2018-02-10 13:57:54.262879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89c1b43b8dd0'
down_revision = '2835da95262c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('StudentFormativeAssessments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('formative_assessment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['formative_assessment_id'], ['formative_assessment.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('StudentFormativeAssessments')
    # ### end Alembic commands ###
