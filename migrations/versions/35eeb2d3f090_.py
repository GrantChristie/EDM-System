"""empty message

Revision ID: 35eeb2d3f090
Revises: bc2fd997ae24
Create Date: 2018-02-10 12:20:54.841262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35eeb2d3f090'
down_revision = 'bc2fd997ae24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('programme_courses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('programme_id', sa.Integer(), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ),
    sa.ForeignKeyConstraint(['programme_id'], ['programme.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('enrollment')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('enrollment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('programme_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], name='enrollment_course_id_fkey'),
    sa.ForeignKeyConstraint(['programme_id'], ['programme.id'], name='enrollment_programme_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='enrollment_pkey')
    )
    op.drop_table('programme_courses')
    # ### end Alembic commands ###