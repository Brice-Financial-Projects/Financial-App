"""update db on laptop

Revision ID: 29d276b9e0f6
Revises: df49b7743c38
Create Date: 2025-04-23 02:12:20.415220

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '29d276b9e0f6'
down_revision = 'df49b7743c38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    op.drop_table('user')
    with op.batch_alter_table('budget_items', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.alter_column('preferred_payment',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)

    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('gross_income', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('retirement_contribution', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('benefit_deductions', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
        batch_op.create_unique_constraint('unique_user_budget_name', ['user_id', 'name'])
        batch_op.create_foreign_key(None, 'profiles', ['profile_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint('unique_user_budget_name', type_='unique')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
        batch_op.drop_column('status')
        batch_op.drop_column('benefit_deductions')
        batch_op.drop_column('retirement_contribution')
        batch_op.drop_column('gross_income')
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('budget_items', schema=None) as batch_op:
        batch_op.alter_column('preferred_payment',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)

    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('username', name='user_username_key')
    )
    op.drop_table('other_income')
    op.drop_table('gross_income')
    op.drop_table('profiles')
    # ### end Alembic commands ###
