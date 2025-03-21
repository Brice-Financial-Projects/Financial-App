"""
A calculator class for handling budget-related financial calculations.

This class provides comprehensive functionality for calculating various aspects of a budget,
including gross income, deductions, taxes, and net income across different payment schedules
(annual, monthly, biweekly).

Attributes:
    budget: Budget instance containing the base financial data
    tax_client: TaxRateClient instance for tax-related calculations
    schedule_multipliers: Dictionary mapping payment schedules to their multipliers

Methods:
    calculate_gross_income: Computes total gross income from all sources
    calculate_pre_tax_deductions: Determines all pre-tax deductions
    calculate_taxable_income: Computes income subject to taxation
    calculate_tax_withholdings: Calculates tax withholdings
    calculate_net_income: Determines final net income across payment periods

Example:
    calculator = BudgetCalculator(budget_id=1)
    net_income = calculator.calculate_net_income()
    annual_net = net_income['annual']['net']
    monthly_net = net_income['monthly']['net']

Notes:
    - All monetary calculations are performed using Decimal for precision
    - Supports various payment schedules defined in PaymentSchedule enum
    - Integrates with tax calculation service for accurate withholding estimates
"""

# app/budget/budget_logic.py

from enum import Enum
from typing import TypedDict, Dict
from decimal import Decimal, InvalidOperation, DivisionByZero
from dataclasses import dataclass

from app.api.tax_rates.client import TaxRateClient
from app.models import Budget, Income, OtherIncome


class PaymentSchedule(Enum):
    """
    Represents various payment schedules.

    This enumeration defines several payment schedule intervals, providing options for
    defining how frequently payments occur. It can be used in financial applications
    to standardize and categorize payment frequencies.
    """
    ANNUALLY = "annually"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    BIWEEKLY = "biweekly"
    WEEKLY = "weekly"


class BudgetCalculator:
    def __init__(self, budget_id: int):
        self.budget = Budget.query.get(budget_id)
        self.tax_client = TaxRateClient()

        self.schedule_multipliers = {
            PaymentSchedule.ANNUALLY: Decimal('1'),
            PaymentSchedule.MONTHLY: Decimal('12'),
            PaymentSchedule.BIMONTHLY: Decimal('24'),
            PaymentSchedule.BIWEEKLY: Decimal('26'),
            PaymentSchedule.WEEKLY: Decimal('52')
        }

    def calculate_gross_income(self) -> Dict[str, Decimal]:
        """Calculate total gross income from all sources"""
        annual_income = Decimal('0')
        income_breakdown = {}

        # Primary Income (W2)
        if self.budget.primary_income:
            schedule = PaymentSchedule(self.budget.primary_income.payment_schedule)
            annual_amount = (Decimal(str(self.budget.primary_income.amount)) *
                             self.schedule_multipliers[schedule])
            income_breakdown['primary_income'] = annual_amount
            annual_income += annual_amount

        # Other Income Sources
        for income in self.budget.other_incomes:
            schedule = PaymentSchedule(income.payment_schedule)
            annual_amount = (Decimal(str(income.amount)) *
                             self.schedule_multipliers[schedule])

            income_breakdown[income.income_type] = annual_amount
            annual_income += annual_amount

        return {
            'total_annual_gross': annual_income,
            'breakdown': income_breakdown
        }

    def calculate_pre_tax_deductions(self) -> Dict[str, Decimal]:
        """Calculate all pre-tax deductions"""
        deductions = {
            'retirement': Decimal('0'),
            'health_insurance': Decimal('0'),
            'fsa_hsa': Decimal('0'),
            'other_benefits': Decimal('0')
        }

        # Retirement Contributions
        if self.budget.retirement_contributions:
            for contribution in self.budget.retirement_contributions:
                schedule = PaymentSchedule(contribution.payment_schedule)
                annual_amount = (Decimal(str(contribution.amount)) *
                                 self.schedule_multipliers[schedule])
                deductions['retirement'] += annual_amount

        # Health Insurance Premiums
        if self.budget.health_insurance:
            schedule = PaymentSchedule(self.budget.health_insurance.payment_schedule)
            annual_amount = (Decimal(str(self.budget.health_insurance.amount)) *
                             self.schedule_multipliers[schedule])
            deductions['health_insurance'] = annual_amount

        # FSA/HSA Contributions
        if self.budget.fsa_hsa_contributions:
            schedule = PaymentSchedule(self.budget.fsa_hsa_contributions.payment_schedule)
            annual_amount = (Decimal(str(self.budget.fsa_hsa_contributions.amount)) *
                             self.schedule_multipliers[schedule])
            deductions['fsa_hsa'] = annual_amount

        # Other Pre-tax Benefits
        if self.budget.other_pretax_benefits:
            for benefit in self.budget.other_pretax_benefits:
                schedule = PaymentSchedule(benefit.payment_schedule)
                annual_amount = (Decimal(str(benefit.amount)) *
                                 self.schedule_multipliers[schedule])
                deductions['other_benefits'] += annual_amount

        deductions['total_deductions'] = sum(deductions.values())
        return deductions

    def calculate_taxable_income(self) -> Dict[str, Decimal]:
        """Calculate taxable income after pre-tax deductions"""
        gross_income = self.calculate_gross_income()
        pre_tax_deductions = self.calculate_pre_tax_deductions()

        taxable_income = gross_income['total_annual_gross'] - pre_tax_deductions['total_deductions']

        return {
            'gross_income': gross_income['total_annual_gross'],
            'pre_tax_deductions': pre_tax_deductions['total_deductions'],
            'taxable_income': taxable_income
        }

    def calculate_tax_withholdings(self) -> Dict[str, Decimal]:
        """Calculate current tax withholdings"""
        withholdings = {
            'federal': Decimal('0'),
            'state': Decimal('0'),
            'local': Decimal('0'),
            'fica': Decimal('0')
        }

        # Get withholdings from primary income
        if self.budget.primary_income and self.budget.primary_income.tax_withholdings:
            w = self.budget.primary_income.tax_withholdings
            schedule = PaymentSchedule(self.budget.primary_income.payment_schedule)
            multiplier = self.schedule_multipliers[schedule]

            withholdings['federal'] += Decimal(str(w.federal)) * multiplier
            withholdings['state'] += Decimal(str(w.state)) * multiplier
            withholdings['local'] += Decimal(str(w.local)) * multiplier
            withholdings['fica'] += Decimal(str(w.fica)) * multiplier

        # Add withholdings from other income sources if applicable
        for income in self.budget.other_incomes:
            if income.tax_withholdings:
                w = income.tax_withholdings
                schedule = PaymentSchedule(income.payment_schedule)
                multiplier = self.schedule_multipliers[schedule]

                withholdings['federal'] += Decimal(str(w.federal)) * multiplier
                withholdings['state'] += Decimal(str(w.state)) * multiplier
                withholdings['local'] += Decimal(str(w.local)) * multiplier
                withholdings['fica'] += Decimal(str(w.fica)) * multiplier

        withholdings['total_withholdings'] = sum(withholdings.values())
        return withholdings


@dataclass
class IncomeComponents:
    gross: Decimal
    deductions: Decimal
    taxable: Decimal
    withholdings: Decimal
    net: Decimal


class IncomeBreakdown(TypedDict):
    gross: Decimal
    pre_tax_deductions: Decimal
    taxable_income: Decimal
    tax_withholdings: Decimal
    net: Decimal


class NetIncomeResult(TypedDict):
    annual: IncomeBreakdown
    monthly: IncomeBreakdown
    biweekly: IncomeBreakdown


def calculate_net_income(self) -> NetIncomeResult:
    """
    Calculate net income across different payment periods.

    Returns:
        NetIncomeResult: Dictionary containing income breakdowns for annual,
                        monthly, and biweekly periods.

    Raises:
        ValueError: If any of the required income calculations return invalid data
        decimal.DivisionByZero: If there's an attempt to divide by zero
        decimal.InvalidOperation: If there's an invalid decimal operation
    """
    try:
        # Get all components with safe dictionary access
        gross_info = self.calculate_gross_income()
        deductions = self.calculate_pre_tax_deductions()
        taxable_info = self.calculate_taxable_income()
        withholdings = self.calculate_tax_withholdings()

        # Validate and extract required values
        annual_gross = Decimal(str(gross_info.get('total_annual_gross', 0)))
        total_deductions = Decimal(str(deductions.get('total_deductions', 0)))
        taxable_income = Decimal(str(taxable_info.get('taxable_income', 0)))
        total_withholdings = Decimal(str(withholdings.get('total_withholdings', 0)))

        # Validate inputs
        if annual_gross < 0 or total_deductions < 0 or total_withholdings < 0:
            raise ValueError("Negative values found in income calculations")

        # Calculate net income
        net_income = annual_gross - total_deductions - total_withholdings

        # Create base annual breakdown
        annual: IncomeBreakdown = {
            'gross': annual_gross,
            'pre_tax_deductions': total_deductions,
            'taxable_income': taxable_income,
            'tax_withholdings': total_withholdings,
            'net': net_income
        }

        # Calculate periodic breakdowns
        monthly_divisor = Decimal('12')
        biweekly_divisor = Decimal('26')

        def calculate_periodic(amount: Decimal, divisor: Decimal) -> Decimal:
            return (amount / divisor).quantize(Decimal('.01'))

        monthly: IncomeBreakdown = {
            'gross': calculate_periodic(annual_gross, monthly_divisor),
            'pre_tax_deductions': calculate_periodic(total_deductions, monthly_divisor),
            'taxable_income': calculate_periodic(taxable_income, monthly_divisor),
            'tax_withholdings': calculate_periodic(total_withholdings, monthly_divisor),
            'net': calculate_periodic(net_income, monthly_divisor)
        }

        biweekly: IncomeBreakdown = {
            'gross': calculate_periodic(annual_gross, biweekly_divisor),
            'pre_tax_deductions': calculate_periodic(total_deductions, biweekly_divisor),
            'taxable_income': calculate_periodic(taxable_income, biweekly_divisor),
            'tax_withholdings': calculate_periodic(total_withholdings, biweekly_divisor),
            'net': calculate_periodic(net_income, biweekly_divisor)
        }

        return {
            'annual': annual,
            'monthly': monthly,
            'biweekly': biweekly
        }

    except KeyError as e:
        raise ValueError(f"Missing required income data: {str(e)}")
    except (InvalidOperation, DivisionByZero) as e:
        raise ValueError(f"Invalid calculation: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error calculating net income: {str(e)}")
