"""Add history table

Revision ID: 39cdd7b3d498
Revises: f33ced38b24c
Create Date: 2023-09-06 16:28:04.604998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '39cdd7b3d498'
down_revision: Union[str, None] = 'f33ced38b24c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'accounthistory',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            'user_login', sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_accounthistory_id'), 'accounthistory', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_accounthistory_id'), table_name='accounthistory')
    op.drop_table('accounthistory')
    # ### end Alembic commands ###
