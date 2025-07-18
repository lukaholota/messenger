"""chat_id_denormalization_message_delivery

Revision ID: 423f34e174a4
Revises: 4809c589aafc
Create Date: 2025-06-25 15:46:27.397011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '423f34e174a4'
down_revision: Union[str, None] = '4809c589aafc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message_delivery', sa.Column('chat_id', sa.Integer(), nullable=True))

    op.execute("""
        UPDATE message_delivery md
        JOIN message m ON m.message_id = md.message_id
        SET md.chat_id = m.chat_id
    """)

    op.alter_column('message_delivery', 'chat_id', existing_type=sa.Integer(), nullable=False)


    op.create_foreign_key('chat_id_fk', 'message_delivery', 'chat', ['chat_id'], ['chat_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('chat_id_fk', 'message_delivery', type_='foreignkey')
    op.drop_column('message_delivery', 'chat_id')
    # ### end Alembic commands ###
