"""Add tax-related fields to Profile model

Revision ID: 541bf19e0984
Revises: 004e1403feba
Create Date: 2025-03-18 13:03:50.985691

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '541bf19e0984'
down_revision = '004e1403feba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # First update any NULL updated_at values to current timestamp
    op.execute("UPDATE budgets SET updated_at = created_at WHERE updated_at IS NULL")
    
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.create_unique_constraint('unique_user_budget_name', ['user_id', 'name'])

    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('is_blind', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('is_student', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('filing_status', sa.String(length=20), nullable=False, server_default='single'))
        batch_op.add_column(sa.Column('num_dependents', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('federal_additional_withholding', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('state_additional_withholding', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('health_insurance_premium', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('hsa_contribution', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('fsa_contribution', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('other_pretax_benefits', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.drop_column('tax_withholding')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tax_withholding', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        batch_op.drop_column('other_pretax_benefits')
        batch_op.drop_column('fsa_contribution')
        batch_op.drop_column('hsa_contribution')
        batch_op.drop_column('health_insurance_premium')
        batch_op.drop_column('state_additional_withholding')
        batch_op.drop_column('federal_additional_withholding')
        batch_op.drop_column('num_dependents')
        batch_op.drop_column('filing_status')
        batch_op.drop_column('is_student')
        batch_op.drop_column('is_blind')
        batch_op.drop_column('date_of_birth')

    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.drop_constraint('unique_user_budget_name', type_='unique')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)

    # ### end Alembic commands ###
