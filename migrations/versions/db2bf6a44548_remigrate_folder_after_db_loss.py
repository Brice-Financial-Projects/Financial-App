"""remigrate folder after db loss

Revision ID: db2bf6a44548
Revises: e75a70a359d1
Create Date: 2025-03-25 19:16:40.139100

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'db2bf6a44548'
down_revision = 'e75a70a359d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # First drop the dependent table
    op.drop_table('state_tax_brackets')
    # Then drop the parent table
    op.drop_table('state_info')
    
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('is_blind', sa.Boolean(), nullable=True),
    sa.Column('is_student', sa.Boolean(), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=False),
    sa.Column('filing_status', sa.String(length=20), nullable=False),
    sa.Column('num_dependents', sa.Integer(), nullable=True),
    sa.Column('income_type', sa.String(length=20), nullable=False),
    sa.Column('pay_cycle', sa.String(length=20), nullable=False),
    sa.Column('federal_additional_withholding', sa.Float(), nullable=True),
    sa.Column('state_additional_withholding', sa.Float(), nullable=True),
    sa.Column('retirement_contribution_type', sa.String(length=10), nullable=False),
    sa.Column('retirement_contribution', sa.Float(), nullable=True),
    sa.Column('health_insurance_premium', sa.Float(), nullable=True),
    sa.Column('hsa_contribution', sa.Float(), nullable=True),
    sa.Column('fsa_contribution', sa.Float(), nullable=True),
    sa.Column('other_pretax_benefits', sa.Float(), nullable=True),
    sa.Column('benefit_deductions', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('budgets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('gross_income', sa.Float(), nullable=False),
    sa.Column('retirement_contribution', sa.Float(), nullable=True),
    sa.Column('benefit_deductions', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'name', name='unique_user_budget_name')
    )
    op.create_table('budget_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('minimum_payment', sa.Float(), nullable=False),
    sa.Column('preferred_payment', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gross_income',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('source', sa.String(length=100), nullable=False),
    sa.Column('gross_income', sa.Float(), nullable=False),
    sa.Column('frequency', sa.String(length=20), nullable=False),
    sa.Column('tax_type', sa.String(length=50), nullable=False),
    sa.Column('state_tax_ref', sa.String(length=2), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('other_income',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('source', sa.String(length=100), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('frequency', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('state_tax_brackets',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('state', sa.VARCHAR(length=2), autoincrement=False, nullable=False),
    sa.Column('tax_year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('bracket_floor', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('rate', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['state'], ['state_info.state_code'], name='state_tax_brackets_state_fkey'),
    sa.PrimaryKeyConstraint('id', name='state_tax_brackets_pkey')
    )
    op.create_table('state_info',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('state_code', sa.VARCHAR(length=2), autoincrement=False, nullable=False),
    sa.Column('state_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('has_state_tax', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='state_info_pkey'),
    sa.UniqueConstraint('state_code', name='state_info_state_code_key')
    )
    op.drop_table('other_income')
    op.drop_table('gross_income')
    op.drop_table('budget_items')
    op.drop_table('budgets')
    op.drop_table('profiles')
    op.drop_table('users')
    # ### end Alembic commands ###
