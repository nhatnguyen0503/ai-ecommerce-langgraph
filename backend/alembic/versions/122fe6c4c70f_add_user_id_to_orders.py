"""add user_id to orders

Revision ID: 122fe6c4c70f
Revises: 4ecdca8e51cc
Create Date: 2026-11-06 15:45:17.332520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '122fe6c4c70f'
down_revision: Union[str, Sequence[str], None] = '4ecdca8e51cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_orders_user_id", ["user_id"])
        batch_op.create_foreign_key("fk_orders_user_id_users", "users", ["user_id"], ["id"])

    # Backfill: link existing orders to the account with the same email.
    op.execute(
        """
        UPDATE orders
        SET user_id = (SELECT users.id FROM users WHERE users.email = orders.customer_email)
        WHERE user_id IS NULL
        """
    )


def downgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint("fk_orders_user_id_users", type_="foreignkey")
        batch_op.drop_index("ix_orders_user_id")
        batch_op.drop_column("user_id")
