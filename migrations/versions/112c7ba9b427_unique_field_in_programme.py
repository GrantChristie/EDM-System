"""unique field in programme

Revision ID: 112c7ba9b427
Revises: 53702e04ecbe
Create Date: 2018-02-15 12:46:04.965786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '112c7ba9b427'
down_revision = '53702e04ecbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'programme', ['programme_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'programme', type_='unique')
    # ### end Alembic commands ###
