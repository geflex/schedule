"""empty message

Revision ID: d3831c0f1018
Revises: 9359a07c044a
Create Date: 2020-12-20 21:48:18.019447

"""

import pathlib
import sys; sys.path.append(str(pathlib.Path().absolute()))
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd3831c0f1018'
down_revision = '9359a07c044a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lessons', sa.Column('weekday_num', sa.Integer(), nullable=True))
    op.drop_column('lessons', 'weekday')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lessons', sa.Column('weekday', postgresql.ENUM('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', name='weekday'), autoincrement=False, nullable=True))
    op.drop_column('lessons', 'weekday_num')
    # ### end Alembic commands ###
