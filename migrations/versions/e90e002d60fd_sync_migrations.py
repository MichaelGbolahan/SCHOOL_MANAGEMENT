"""Sync migrations

Revision ID: e90e002d60fd
Revises: 779a39a651ee
Create Date: 2024-11-17 17:45:00.116260

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e90e002d60fd'
down_revision = '779a39a651ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('school_fee', 'student_register_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key(None, 'school_fee', 'department', ['department_id'], ['id'])
    op.create_foreign_key(None, 'school_fee', 'student_register', ['student_register_id'], ['id'])
    op.create_foreign_key(None, 'school_fee', 'programme', ['programme_id'], ['id'])
    op.drop_column('school_fee', 'program')
    op.drop_column('school_fee', 'academic_session')
    op.drop_column('school_fee', 'created_at')
    op.drop_column('school_fee', 'level')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('school_fee', sa.Column('level', mysql.VARCHAR(length=50), nullable=False))
    op.add_column('school_fee', sa.Column('created_at', mysql.DATETIME(), nullable=True))
    op.add_column('school_fee', sa.Column('academic_session', mysql.VARCHAR(length=20), nullable=False))
    op.add_column('school_fee', sa.Column('program', mysql.VARCHAR(length=100), nullable=False))
    op.drop_constraint(None, 'school_fee', type_='foreignkey')
    op.drop_constraint(None, 'school_fee', type_='foreignkey')
    op.drop_constraint(None, 'school_fee', type_='foreignkey')
    op.alter_column('school_fee', 'student_register_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###
