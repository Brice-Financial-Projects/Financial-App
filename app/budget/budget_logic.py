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
from datetime import datetime
from enum import Enum
from typing import TypedDict, Dict, Any
from decimal import Decimal, InvalidOperation, DivisionByZero
from dataclasses import dataclass
from app.models import Budget, GrossIncome, OtherIncome, Profile, BudgetItem
from flask import current_app

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
        self.schedule_multipliers = {
            PaymentSchedule.ANNUALLY.value: Decimal('1'),
            PaymentSchedule.MONTHLY.value: Decimal('12'),
            PaymentSchedule.BIMONTHLY.value: Decimal('24'),
            PaymentSchedule.BIWEEKLY.value: Decimal('26'),
            PaymentSchedule.WEEKLY.value: Decimal('52')
        }

    def validate_budget(self, budget: Budget) -> None:
        """
        Validate the budget instance has required attributes and relationships.
        
        Args:
            budget: Budget instance to validate
            
        Raises:
            ValueError: If budget is invalid or missing required data
        """
        if not budget:
            raise ValueError("Budget instance is required")
            
        if not budget.profile:
            raise ValueError("Budget must have an associated profile")
            
        if not budget.gross_income_sources:
            raise ValueError("Budget must have at least one income source")

    def calculate_gross_income(self):
        """Calculate total gross income from all sources."""
        try:
            total_annual = Decimal('0')
            income_details = []

            # Get all income sources for this budget
            income_sources = GrossIncome.query.filter_by(budget_id=self.budget.id).all()

            for source in income_sources:
                # Convert to annual amount based on frequency
                base_amount = Decimal(str(source.gross_income))
                if source.frequency == 'weekly':
                    annual_amount = base_amount * Decimal('52')
                elif source.frequency == 'biweekly':
                    annual_amount = base_amount * Decimal('26')
                elif source.frequency == 'monthly':
                    annual_amount = base_amount * Decimal('12')
                elif source.frequency == 'bimonthly':
                    annual_amount = base_amount * Decimal('24')
                else:  # annual
                    annual_amount = base_amount

                total_annual += annual_amount

                # Calculate monthly amount for display
                monthly_amount = annual_amount / Decimal('12')

                income_details.append({
                    'source': source.source,
                    'category': source.category,
                    'annual': annual_amount,
                    'monthly': monthly_amount,
                    'frequency': source.frequency,
                    'tax_type': source.tax_type
                })

            return {
                'annual': total_annual,
                'monthly': total_annual / Decimal('12'),
                'details': income_details
            }
        except Exception as e:
            current_app.logger.error(f"Error calculating gross income: {str(e)}")
            raise

    def calculate_pre_tax_deductions(self) -> Dict[str, Decimal]:
        """Calculate pre-tax deductions including retirement, health insurance, etc."""
        try:
            # Get gross income data
            gross_income_data = self.calculate_gross_income()
            total_annual_gross = Decimal(str(gross_income_data['annual']))

            # Get profile data
            profile = Profile.query.filter_by(id=self.budget.profile_id).first()
            if not profile:
                raise ValueError("No profile found for this budget")

            # Calculate retirement contribution (as percentage of gross income)
            retirement_contribution = Decimal('0')
            if profile.retirement_contribution and profile.retirement_contribution > 0:
                # Convert percentage to decimal and calculate annual amount
                retirement_percentage = Decimal(str(profile.retirement_contribution)) / Decimal('100')
                retirement_contribution = total_annual_gross * retirement_percentage

            # Get other pre-tax deductions
            health_insurance = Decimal(str(profile.health_insurance_premium or 0)) * Decimal('12')  # Convert monthly to annual
            fsa_hsa = Decimal(str((profile.hsa_contribution or 0) + (profile.fsa_contribution or 0))) * Decimal('12')  # Convert monthly to annual
            other_benefits = Decimal(str(profile.other_pretax_benefits or 0)) * Decimal('12')  # Convert monthly to annual

            # Calculate total pre-tax deductions
            total_pre_tax = retirement_contribution + health_insurance + fsa_hsa + other_benefits

            return {
                'retirement': retirement_contribution,
                'health_insurance': health_insurance,
                'fsa_hsa': fsa_hsa,
                'other_benefits': other_benefits,
                'total': total_pre_tax
            }

        except Exception as e:
            current_app.logger.error(f"Error calculating pre-tax deductions: {str(e)}")
            raise

    def calculate_taxable_income(self):
        """Calculate taxable income after pre-tax deductions."""
        try:
            gross_income = self.calculate_gross_income()
            pre_tax_deductions = self.calculate_pre_tax_deductions()
            
            # Use 'annual' instead of 'total_annual_gross'
            taxable_income = gross_income['annual'] - pre_tax_deductions['total']
            
            return {
                'annual': taxable_income,
                'monthly': taxable_income / Decimal('12'),
                'gross_income': gross_income,
                'pre_tax_deductions': pre_tax_deductions
            }
        except Exception as e:
            current_app.logger.error(f"Error calculating taxable income: {str(e)}")
            raise

    def calculate_tax_withholdings(self) -> Dict[str, Decimal]:
        """Calculate tax withholdings based on taxable income."""
        try:
            current_app.logger.debug("Starting tax withholdings calculation")
            
            # Get gross income and taxable income data
            gross_info = self.calculate_gross_income()
            deductions = self.calculate_pre_tax_deductions()
            taxable_info = self.calculate_taxable_income()
            
            # Validate and extract required values
            annual_gross = gross_info['annual']
            total_deductions = deductions['total']
            taxable_income = taxable_info['annual']
            
            # Calculate FICA tax (7.65% of gross income)
            fica_tax = annual_gross * Decimal('0.0765')
            
            # Calculate federal tax using tax brackets
            federal_tax = self._calculate_federal_tax(taxable_income)
            
            # Calculate state tax (simplified - using a flat rate)
            state_tax = taxable_income * Decimal('0.05')  # 5% state tax rate
            
            # Calculate total tax
            total_tax = federal_tax + state_tax + fica_tax
            
            return {
                'federal': federal_tax,
                'state': state_tax,
                'fica': fica_tax,
                'total': total_tax,
                'details': {
                    'gross_income': annual_gross,
                    'pre_tax_deductions': total_deductions,
                    'taxable_income': taxable_income
                }
            }
        except Exception as e:
            current_app.logger.error(f"Error in calculate_tax_withholdings: {str(e)}")
            raise ValueError(f"Error calculating tax withholdings: {str(e)}")

    def _calculate_federal_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate federal tax using 2023 tax brackets"""
        brackets = [
            (Decimal('0'), Decimal('11000'), Decimal('0.10')),
            (Decimal('11000'), Decimal('44725'), Decimal('0.12')),
            (Decimal('44725'), Decimal('95375'), Decimal('0.22')),
            (Decimal('95375'), Decimal('182100'), Decimal('0.24')),
            (Decimal('182100'), Decimal('231250'), Decimal('0.32')),
            (Decimal('231250'), Decimal('578125'), Decimal('0.35')),
            (Decimal('578125'), Decimal('999999999'), Decimal('0.37'))
        ]
        
        tax = Decimal('0')
        remaining_income = taxable_income
        
        for lower, upper, rate in brackets:
            if remaining_income <= 0:
                break
                
            bracket_income = min(remaining_income, upper - lower)
            tax += bracket_income * rate
            remaining_income -= bracket_income
            
        return tax

    def _calculate_state_tax(self, taxable_income: Decimal, state: str) -> Decimal:
        """Calculate state tax based on state"""
        # Simple state tax calculation - should be expanded for accurate state-specific rules
        state_tax_rates = {
            'CA': Decimal('0.093'),  # 9.3% for California
            'NY': Decimal('0.0685'),  # 6.85% for New York
            'TX': Decimal('0'),      # No state income tax
            'FL': Decimal('0'),      # No state income tax
            # Add more states as needed
        }
        
        rate = state_tax_rates.get(state, Decimal('0.05'))  # Default 5% for other states
        return taxable_income * rate

    def _calculate_fica_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate FICA taxes (Social Security and Medicare)"""
        ss_limit = Decimal('160200')  # 2023 Social Security wage base
        ss_rate = Decimal('0.062')    # 6.2%
        medicare_rate = Decimal('0.0145')  # 1.45%
        
        # Calculate Social Security (up to limit)
        ss_taxable = min(taxable_income, ss_limit)
        ss_tax = ss_taxable * ss_rate
        
        # Calculate Medicare (no limit)
        medicare_tax = taxable_income * medicare_rate
        
        return ss_tax + medicare_tax

    def calculate_budget(self) -> Dict[str, Any]:
        """Calculate the final budget with all components."""
        try:
            # Get gross income (already annual)
            gross_income = self.calculate_gross_income()
            total_annual_gross = gross_income['annual']
            total_monthly_gross = total_annual_gross / 12

            # Calculate pre-tax deductions
            deductions = self.calculate_pre_tax_deductions()
            total_annual_deductions = deductions['total']
            total_monthly_deductions = total_annual_deductions / 12

            # Calculate taxable income
            taxable_info = self.calculate_taxable_income()
            total_annual_taxable = taxable_info['taxable_income']
            total_monthly_taxable = total_annual_taxable / 12

            # Calculate tax withholdings
            tax_data = self.calculate_tax_withholdings()
            total_annual_tax = tax_data['total']
            total_monthly_tax = total_annual_tax / 12

            # Calculate net income
            total_annual_net = total_annual_gross - total_annual_deductions - total_annual_tax
            total_monthly_net = total_annual_net / 12

            # Get all budget items
            budget_items = BudgetItem.query.filter_by(budget_id=self.budget.id).all()
            
            # Calculate total expenses
            total_monthly_expenses = sum(float(item.minimum_payment) for item in budget_items)
            
            # Calculate remaining money
            remaining_money = total_monthly_net - total_monthly_expenses

            return {
                'gross_income': {
                    'annual': total_annual_gross,
                    'monthly': total_monthly_gross,
                    'details': gross_income['details']
                },
                'deductions': {
                    'annual': total_annual_deductions,
                    'monthly': total_monthly_deductions,
                    'details': deductions
                },
                'taxable_income': {
                    'annual': total_annual_taxable,
                    'monthly': total_monthly_taxable
                },
                'tax_withholdings': {
                    'annual': total_annual_tax,
                    'monthly': total_monthly_tax,
                    'details': tax_data
                },
                'net_income': {
                    'annual': total_annual_net,
                    'monthly': total_monthly_net
                },
                'expenses': {
                    'total': total_monthly_expenses,
                    'items': budget_items
                },
                'remaining_money': remaining_money
            }

        except Exception as e:
            current_app.logger.error(f"Error calculating budget: {str(e)}")
            raise

    def _convert_to_annual(self, amount: Decimal, frequency: str) -> Decimal:
        """Convert an amount to annual based on frequency"""
        try:
            multiplier = self.schedule_multipliers.get(frequency.lower())
            if multiplier is None:
                logger.warning(f"Unknown frequency '{frequency}', defaulting to annual")
                multiplier = Decimal('1')

            annual_amount = amount * multiplier
            logger.debug(f"Converted {amount} from {frequency} to annual: {annual_amount}")
            return annual_amount
            
        except (TypeError, InvalidOperation) as e:
            logger.error(f"Error converting to annual amount: {str(e)}")
            raise ValueError(f"Error converting to annual amount: {str(e)}")

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
    logger.info(f"Calculating final budget for budget_id: {budget_id}")

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
        annual_gross = Decimal(str(gross_info.get('annual', 0)))
        total_deductions = Decimal(str(deductions.get('total', 0)))
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
