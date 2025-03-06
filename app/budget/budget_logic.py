"""backend/app/budget/budget_logic.py."""

def calculate_budget(user_data):
    """Calculate budget based upon user data."""
    gross_income = user_data.get('income', 0)
    pay_period = user_data.get('pay_period', 'monthly')

    # Validate gross_income
    if gross_income <= 0:
        raise ValueError("Income must be greater than zero.")

    # Calculate monthly income
    if pay_period == 'biweekly':
        monthly_income = (gross_income / 26) * 2
    elif pay_period == 'semimonthly':
        monthly_income = gross_income / 24
    elif pay_period == 'weekly':
        monthly_income = (gross_income / 52) * 4
    else:  # monthly
        monthly_income = gross_income / 12

    net_income = monthly_income * 0.78

    # Handle missing categories
    utilities = user_data.get('utilities', {})
    debts = user_data.get('debts', {})
    loans = user_data.get('loans', {})
    groceries = user_data.get('groceries', 0)
    transportation = user_data.get('transportation', 0)

    # Calculate expenses
    total_expenses = (
        user_data.get('rent', 0) +
        sum(utilities.values()) +
        sum(debts.values()) +
        sum(loans.values()) +
        groceries +
        transportation
    )

    # Calculate income-to-debt ratio
    total_debts = sum(debts.values()) + sum(loans.values())
    income_to_debt_ratio = total_debts / monthly_income if monthly_income > 0 else 0

    return {
        'monthly_income': monthly_income,
        'net_income': net_income,
        'total_expenses': total_expenses,
        'remaining_money': net_income - total_expenses,
        'income_to_debt_ratio': income_to_debt_ratio,
        'details': user_data
    }



def create_excel(budget_data):
    """Export budget results to an Excel spreadsheet."""
    from flask import make_response
    import pandas as pd
    from io import BytesIO

    # Separate budget details
    summary_data = {
        'Monthly Income': budget_data['monthly_income'],
        'Net Income': budget_data['net_income'],
        'Total Expenses': budget_data['total_expenses'],
        'Remaining Money': budget_data['remaining_money'],
        'Income-to-Debt Ratio': budget_data['income_to_debt_ratio']
    }
    details_data = pd.DataFrame(budget_data['details']).transpose().reset_index()
    details_data.columns = ['Category', 'Value']

    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write summary and details to separate sheets
        pd.DataFrame([summary_data]).to_excel(writer, index=False, sheet_name='Summary')
        details_data.to_excel(writer, index=False, sheet_name='Details')

    output.seek(0)

    # Create Flask response
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=budget.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response


