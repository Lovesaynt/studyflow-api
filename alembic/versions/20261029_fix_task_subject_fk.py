"""Fix task-subject foreign key to simple FK

Revision ID: fix_task_subject_fk
Revises: 557bda9b65ce
Create Date: 2026-10-29

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_task_subject_fk"
down_revision = "557bda9b65ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the composite foreign key constraint
    op.drop_constraint("fk_task_subject_user", "tasks", type_="foreignkey")

    # Add a simple foreign key from tasks.subject_id to subjects.id
    op.create_foreign_key(
        "fk_task_subject", "tasks", "subjects", ["subject_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    # Drop the simple foreign key
    op.drop_constraint("fk_task_subject", "tasks", type_="foreignkey")

    # Recreate the composite foreign key
    op.create_foreign_key(
        "fk_task_subject_user",
        "tasks",
        "subjects",
        ["subject_id", "user_id"],
        ["id", "user_id"],
        ondelete="SET NULL",
    )
