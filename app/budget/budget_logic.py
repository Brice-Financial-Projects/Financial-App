"""backend/app/budget/budget_logic.py."""
import requests
import json
from datetime import datetime
import os
import math

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


def calculate_tax_withdrawals(budget, income_sources, profile):
    """Calculate tax withdrawals based on state and income types."""
    # Default state tax rates - a simplified approximation
    # In a production environment, this would be connected to a tax API
    state_tax_rates = {
        "AL": 0.05, "AK": 0.00, "AZ": 0.045, "AR": 0.065, "CA": 0.093, 
        "CO": 0.0463, "CT": 0.0699, "DE": 0.0660, "FL": 0.00, "GA": 0.0575,
        "HI": 0.11, "ID": 0.0693, "IL": 0.0495, "IN": 0.0323, "IA": 0.0853,
        "KS": 0.057, "KY": 0.05, "LA": 0.0425, "ME": 0.0715, "MD": 0.0575,
        "MA": 0.05, "MI": 0.0425, "MN": 0.0985, "MS": 0.05, "MO": 0.054,
        "MT": 0.0675, "NE": 0.0684, "NV": 0.00, "NH": 0.05, "NJ": 0.1075,
        "NM": 0.0590, "NY": 0.1082, "NC": 0.0525, "ND": 0.0290, "OH": 0.0399,
        "OK": 0.0475, "OR": 0.099, "PA": 0.0307, "RI": 0.0599, "SC": 0.07,
        "SD": 0.00, "TN": 0.00, "TX": 0.00, "UT": 0.0495, "VT": 0.0875,
        "VA": 0.0575, "WA": 0.00, "WV": 0.065, "WI": 0.0765, "WY": 0.00,
        "DC": 0.0895
    }
    
    # Get state from profile
    state = profile.state.upper()
    state_tax_rate = state_tax_rates.get(state, 0.05)  # Default to 5% if state not found
    
    # Initialize return data
    tax_data = {
        'state': state,
        'income_details': [],
        'total_annual_gross': 0,
        'total_annual_federal_tax': 0,
        'total_annual_state_tax': 0,
        'total_annual_fica_tax': 0,
        'total_annual_net': 0,
        'total_monthly_gross': 0,
        'total_monthly_federal_tax': 0,
        'total_monthly_state_tax': 0,
        'total_monthly_fica_tax': 0,
        'total_monthly_net': 0
    }
    
    # Calculate tax for each income source
    for income in income_sources:
        # Convert income to annual based on frequency
        annual_gross = convert_to_annual(income.gross_income, income.frequency)
        
        # Calculate taxes based on income type
        if income.tax_type == "W2":
            # W2 income is subject to all taxes
            federal_tax = calculate_federal_tax(annual_gross)
            state_tax = annual_gross * state_tax_rate
            fica_tax = calculate_fica_tax(annual_gross)
        elif income.tax_type == "Self-Employed":
            # Self-employed pays both employer and employee FICA
            federal_tax = calculate_federal_tax(annual_gross)
            state_tax = annual_gross * state_tax_rate
            fica_tax = calculate_fica_tax(annual_gross) * 2  # Double FICA for self-employed
        else:
            # Other income might have different tax treatments
            federal_tax = calculate_federal_tax(annual_gross) * 0.85  # Simplified
            state_tax = annual_gross * state_tax_rate
            fica_tax = 0  # No FICA tax on non-earned income
        
        # Calculate net income
        annual_net = annual_gross - federal_tax - state_tax - fica_tax
        
        # Convert to monthly for consistency
        monthly_gross = annual_gross / 12
        monthly_federal_tax = federal_tax / 12
        monthly_state_tax = state_tax / 12
        monthly_fica_tax = fica_tax / 12
        monthly_net = annual_net / 12
        
        # Add to income details
        tax_data['income_details'].append({
            'source': income.source,
            'gross_income': monthly_gross,
            'federal_tax': monthly_federal_tax,
            'state_tax': monthly_state_tax,
            'fica_tax': monthly_fica_tax,
            'net_income': monthly_net
        })
        
        # Add to totals
        tax_data['total_annual_gross'] += annual_gross
        tax_data['total_annual_federal_tax'] += federal_tax
        tax_data['total_annual_state_tax'] += state_tax
        tax_data['total_annual_fica_tax'] += fica_tax
        tax_data['total_annual_net'] += annual_net
    
    # Calculate monthly totals
    tax_data['total_monthly_gross'] = tax_data['total_annual_gross'] / 12
    tax_data['total_monthly_federal_tax'] = tax_data['total_annual_federal_tax'] / 12
    tax_data['total_monthly_state_tax'] = tax_data['total_annual_state_tax'] / 12
    tax_data['total_monthly_fica_tax'] = tax_data['total_annual_fica_tax'] / 12
    tax_data['total_monthly_net'] = tax_data['total_annual_net'] / 12
    
    return tax_data


def calculate_federal_tax(annual_income):
    """Calculate federal tax based on 2023 tax brackets (simplified)."""
    # 2023 tax brackets for single filers (simplified)
    if annual_income <= 11000:
        return annual_income * 0.10
    elif annual_income <= 44725:
        return 1100 + (annual_income - 11000) * 0.12
    elif annual_income <= 95375:
        return 5147 + (annual_income - 44725) * 0.22
    elif annual_income <= 182100:
        return 16290 + (annual_income - 95375) * 0.24
    elif annual_income <= 231250:
        return 37104 + (annual_income - 182100) * 0.32
    elif annual_income <= 578125:
        return 52832 + (annual_income - 231250) * 0.35
    else:
        return 174238.25 + (annual_income - 578125) * 0.37


def calculate_fica_tax(annual_income):
    """Calculate FICA tax (Social Security and Medicare)."""
    # Social Security tax is 6.2% up to cap
    ss_cap = 160200  # 2023 Social Security wage base
    ss_tax = min(annual_income, ss_cap) * 0.062
    
    # Medicare tax is 1.45% on all earned income
    medicare_tax = annual_income * 0.0145
    
    # Additional Medicare tax of 0.9% on income above $200,000
    if annual_income > 200000:
        medicare_tax += (annual_income - 200000) * 0.009
    
    return ss_tax + medicare_tax


def convert_to_annual(amount, frequency):
    """Convert an amount based on frequency to annual amount."""
    if frequency == 'weekly':
        return amount * 52
    elif frequency == 'biweekly':
        return amount * 26
    elif frequency == 'monthly':
        return amount * 12
    elif frequency == 'bimonthly':
        return amount * 24
    elif frequency == 'annually':
        return amount
    else:
        return amount * 12  # Default to monthly


def calculate_final_budget(budget, income_sources, budget_items, tax_data, profile):
    """Calculate the final budget with all deductions and expenses."""
    # Get net income from tax calculation
    monthly_net_income = tax_data['total_monthly_net']
    
    # Subtract retirement contributions and benefit deductions
    retirement_contribution = profile.retirement_contribution
    benefit_deductions = profile.benefit_deductions
    
    # Calculate adjusted net income
    adjusted_net_income = monthly_net_income - retirement_contribution - benefit_deductions
    
    # Calculate total expenses by category
    expenses_by_category = {}
    for item in budget_items:
        # Use preferred payment if available, otherwise minimum payment
        expense_amount = item.preferred_payment if item.preferred_payment > 0 else item.minimum_payment
        
        if item.category not in expenses_by_category:
            expenses_by_category[item.category] = 0
        expenses_by_category[item.category] += expense_amount
    
    # Calculate total expenses
    total_expenses = sum(expenses_by_category.values())
    
    # Calculate remaining money
    remaining_money = adjusted_net_income - total_expenses
    
    # Create budget result
    budget_result = {
        'monthly_gross_income': tax_data['total_monthly_gross'],
        'monthly_tax_withholding': (
            tax_data['total_monthly_federal_tax'] + 
            tax_data['total_monthly_state_tax'] + 
            tax_data['total_monthly_fica_tax']
        ),
        'retirement_contribution': retirement_contribution,
        'benefit_deductions': benefit_deductions,
        'monthly_net_income': adjusted_net_income,
        'total_expenses': total_expenses,
        'expenses_by_category': expenses_by_category,
        'remaining_money': remaining_money
    }
    
    return budget_result


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


