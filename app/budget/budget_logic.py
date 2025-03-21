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

import logging
from enum import Enum
from typing import TypedDict, Dict
from decimal import Decimal, InvalidOperation, DivisionByZero
from dataclasses import dataclass
from functools import lru_cache

from app.api.tax_rates.client import TaxRateClient
from app.models import Budget, GrossIncome, OtherIncome

logger = logging.getLogger(__name__)

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
    def __init__(self, budget: Budget):
        """
        Initialize the BudgetCalculator with a budget instance.

        Args:
            budget: Budget instance containing the financial data
        """
        self.budget = budget
        self.validate_budget(budget)
        self.tax_client = TaxRateClient()
        self.schedule_multipliers = {
            PaymentSchedule.ANNUALLY: Decimal('1'),
            PaymentSchedule.MONTHLY: Decimal('12'),
            PaymentSchedule.BIWEEKLY: Decimal('26'),
            PaymentSchedule.WEEKLY: Decimal('52')
        }

    def calculate_gross_income(self) -> Dict[str, Decimal]:
        """
        Calculate total gross income including salary and other income sources.

        Returns:
            Dict containing total annual gross income and its components
        """
        try:
            # Get primary income from GrossIncome
            gross_income = GrossIncome.query.filter_by(budget_id=self.budget.id).first()
            if not gross_income:
                raise ValueError("No gross income found for this budget")

            base_salary = Decimal(str(gross_income.amount or 0))

            # Calculate other income
            other_income_total = Decimal('0')
            other_incomes = OtherIncome.query.filter_by(budget_id=self.budget.id).all()

            for income in other_incomes:
                if income.amount:
                    other_amount = Decimal(str(income.amount))
                    # Normalize to annual amount based on payment schedule
                    if income.schedule:
                        multiplier = self.schedule_multipliers.get(income.schedule, Decimal('1'))
                        other_amount *= multiplier
                    other_income_total += other_amount

            total_annual_gross = base_salary + other_income_total

            return {
                'base_salary': base_salary,
                'other_income': other_income_total,
                'total_annual_gross': total_annual_gross
            }

        except (TypeError, ValueError) as e:
            raise ValueError(f"Error calculating gross income: {str(e)}")

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

    @lru_cache(maxsize=128)
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

    @property
    def primary_income(self):
        return GrossIncome.query.filter_by(budget_id=self.id, category="W2 Job").first()

    @property
    def other_incomes(self):
        return GrossIncome.query.filter_by(budget_id=self.id).filter(GrossIncome.category != "W2 Job").all()

    @staticmethod
    def validate_budget(budget):
        if not budget.gross_income_sources:
            raise ValueError("Budget must have at least one income source")
        if not budget.profile:
            raise ValueError("Budget must have an associated profile")


def calculate_budget(budget_id: int) -> Dict:
    """
    Standalone function that uses BudgetCalculator to calculate budget details.

    Args:
        budget_id: ID of the budget to calculate

    Returns:
        Dictionary containing all budget calculations based on user input
    """
    logger.info(f"Calculating final budget for budget_id: {self.budget.id}")

    try:
        budget = Budget.query.get_or_404(budget_id)
        calculator = BudgetCalculator(budget)
        return calculator.calculate_budget()
    except Exception as e:
        logger.error(f"Error calculating budget: {str(e)}")
        raise ValueError(f"Error calculating budget: {str(e)}")


def create_excel(budget_data: Dict) -> bytes:
    """
    Standalone function that uses BudgetCalculator to create Excel file.

    Args:
        budget_data: Dictionary containing budget data

    Returns:
        Excel file as bytes
    """
    try:
        calculator = BudgetCalculator(budget_data['budget'])
        return calculator.create_excel()
    except Exception as e:
        raise ValueError(f"Error creating Excel file: {str(e)}")


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



# Explicitly export these functions
__all__ = ['calculate_budget', 'create_excel']
