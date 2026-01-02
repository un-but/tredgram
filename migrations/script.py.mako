"""${message if message.endswith(".") else f"{message}."}

ID миграции: ${up_revision}
Изменяет: ${"-" if not down_revision else down_revision | comma,n}
Дата создания: ${create_date.strftime("%H:%M:%S %d.%m.%Y")} по МСК
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
% if imports:
${imports}
% endif

# Идентификаторы миграции, используются Alembic.
revision: str = ${repr(up_revision).replace("'", "\"")}
down_revision: str | None = ${repr(down_revision).replace("'", "\"")}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels).replace("'", "\"")}
depends_on: str | Sequence[str] | None = ${repr(depends_on).replace("'", "\"")}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades.replace("'", "\"") if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades.replace("'", "\"") if downgrades else "pass"}
