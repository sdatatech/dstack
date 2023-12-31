"""Add ssh keys to project

Revision ID: 32e5940896ad
Revises: e6df5271c730
Create Date: 2023-08-17 16:05:15.118951

"""
import sqlalchemy as sa
from alembic import op

from dstack._internal.utils.crypto import generate_rsa_key_pair_bytes

# revision identifiers, used by Alembic.
revision = "32e5940896ad"
down_revision = "e6df5271c730"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.add_column(sa.Column("ssh_private_key", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("ssh_public_key", sa.Text(), nullable=True))

    t_project = sa.Table(
        "projects",
        sa.MetaData(),
        sa.Column("name", sa.String(50)),
        sa.Column("ssh_private_key", sa.Text()),
        sa.Column("ssh_public_key", sa.Text()),
    )
    conn = op.get_bind()
    projects = conn.execute(sa.select(t_project.c.name)).fetchall()
    for (project,) in projects:
        private_bytes, public_bytes = generate_rsa_key_pair_bytes(comment=f"{project}@dstack")
        conn.execute(
            t_project.update()
            .where(t_project.c.name == project)
            .values(
                ssh_private_key=private_bytes.decode(),
                ssh_public_key=public_bytes.decode(),
            )
        )

    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.alter_column("ssh_private_key", nullable=False)
        batch_op.alter_column("ssh_public_key", nullable=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.drop_column("ssh_public_key")
        batch_op.drop_column("ssh_private_key")

    # ### end Alembic commands ###
