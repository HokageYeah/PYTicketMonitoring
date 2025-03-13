"""insert_initial_test2

Revision ID: dfdaea1dbe4e
Revises: 5276401e84bd
Create Date: 2025-03-13 19:44:33.650943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column
from src.sql.models.test2 import Test2


# revision identifiers, used by Alembic.
revision: str = 'dfdaea1dbe4e'
down_revision: Union[str, None] = '5276401e84bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 插入11 条数据
    test2s = table('test2', column('test2_name'), column('test2_age'))
    test2_data = []
    for i in range(1, 12):
        test2 = {
            "test2_name": f"test2yy_{i}",
            "test2_age": i
        }
        test2_data.append(test2)
    op.bulk_insert(test2s, test2_data)


def downgrade() -> None:
    """Downgrade schema."""
    pass
