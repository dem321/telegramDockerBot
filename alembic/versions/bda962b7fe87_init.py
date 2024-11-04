"""init

Revision ID: bda962b7fe87
Revises: 
Create Date: 2024-11-03 23:47:48.619787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bda962b7fe87'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_name', sa.String(), nullable=True),
    sa.Column('date_added', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chat_config',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.Column('ssh_host', sa.String(), nullable=True),
    sa.Column('ssh_port', sa.Integer(), nullable=True),
    sa.Column('ssh_user', sa.String(), nullable=True),
    sa.Column('ssh_password', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_config')
    op.drop_table('chat')
    # ### end Alembic commands ###
