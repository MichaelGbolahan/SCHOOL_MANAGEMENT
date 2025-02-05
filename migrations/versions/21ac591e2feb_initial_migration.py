"""Initial migration

Revision ID: 21ac591e2feb
Revises: 415cf0869451
Create Date: 2024-11-03 18:02:30.673625

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '21ac591e2feb'
down_revision = '415cf0869451'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('email', table_name='student__register')
    op.drop_table('student__register')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student__register',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('first_name', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('last_name', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('other_name', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('programme_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('session', mysql.VARCHAR(length=60), nullable=True),
    sa.Column('faculty_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('department_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('level', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('sex_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('date_of_birth', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('phone_no', mysql.VARCHAR(length=20), nullable=False),
    sa.Column('residential_address', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('place_of_birth', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('state_of_origin', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('local_govt_area', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('parent_guardian_name', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('parent_guardian_address', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('parent_guardian_phone_no', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('password', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('profile', mysql.VARCHAR(length=180), nullable=False),
    sa.Column('verified', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('verification_code', mysql.VARCHAR(length=6), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], name='student__register_ibfk_3'),
    sa.ForeignKeyConstraint(['faculty_id'], ['faculty.id'], name='student__register_ibfk_2'),
    sa.ForeignKeyConstraint(['programme_id'], ['programme.id'], name='student__register_ibfk_1'),
    sa.ForeignKeyConstraint(['sex_id'], ['sex.id'], name='student__register_ibfk_4'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('email', 'student__register', ['email'], unique=True)
    # ### end Alembic commands ###
