"""create users table

Revision ID: b69e1d1d68ff
Revises: 
Create Date: 2023-12-26 00:18:17.550972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b69e1d1d68ff'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('descriptor', sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('users')
