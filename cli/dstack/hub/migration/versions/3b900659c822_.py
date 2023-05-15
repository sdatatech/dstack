"""empty message

Revision ID: 3b900659c822
Revises: 
Create Date: 2023-04-11 11:23:01.049322

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3b900659c822"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("backend", sa.String(length=30), nullable=False),
        sa.Column("config", sa.String(length=300), nullable=False),
        sa.Column("auth", sa.String(length=300), nullable=False),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_projects")),
    )
    op.create_table(
        "users",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("token", sa.String(length=200), nullable=False),
        sa.Column("global_role", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_users")),
    )
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_name", sa.String(length=50), nullable=False),
        sa.Column("user_name", sa.String(length=50), nullable=False),
        sa.Column("project_role", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_name"],
            ["projects.name"],
            name=op.f("fk_members_project_name_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_name"],
            ["users.name"],
            name=op.f("fk_members_user_name_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_members")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("members")
    op.drop_table("users")
    op.drop_table("projects")
    # ### end Alembic commands ###
