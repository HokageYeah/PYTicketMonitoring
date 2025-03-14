"""insert_initial_test2

Revision ID: 75df7ee3a52c
Revises: e1932a288876
Create Date: 2025-03-14 10:05:48.061118

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import table, column


# revision identifiers, used by Alembic.
revision: str = '75df7ee3a52c'
down_revision: Union[str, None] = 'e1932a288876'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 插入11 条数据
    test2s = table('test2', column('test2_name'), column('test2_age'))
    test2_data = []
    for i in range(1, 12):
        test2 = {
            "test2_name": f"test2_wyj_dev_yy_{i}",
            "test2_age": i
        }
        test2_data.append(test2)
    op.bulk_insert(test2s, test2_data)


def downgrade() -> None:
    """Downgrade schema."""
    pass
