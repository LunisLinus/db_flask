"""merge_multiple_heads

Revision ID: 5eb9998f97a7
Revises: 3caeefc59069, d526288313e6
Create Date: 2025-05-21 06:28:43.475080

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '5eb9998f97a7'
down_revision = ('3caeefc59069', 'd526288313e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
