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
from typing import TypedDict, Dict
from decimal import Decimal, InvalidOperation, DivisionByZero
from dataclasses import dataclass
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

            # Use gross_income field and normalize to annual based on frequency
            base_salary = Decimal(str(gross_income.gross_income or 0))
            if gross_income.frequency:
                multiplier = self.schedule_multipliers.get(gross_income.frequency, Decimal('1'))
                base_salary *= multiplier

            # Calculate other income
            other_income_total = Decimal('0')
            other_incomes = OtherIncome.query.filter_by(budget_id=self.budget.id).all()

            for income in other_incomes:
                if income.amount and income.amount > 0:
                    other_amount = Decimal(str(income.amount))
                    # Normalize to annual amount based on payment schedule
                    if income.frequency:
                        multiplier = self.schedule_multipliers.get(income.frequency, Decimal('1'))
                        other_amount *= multiplier
                    other_income_total += other_amount

            total_annual_gross = base_salary + other_income_total

            return {
                'base_salary': base_salary,
                'other_income': other_income_total,
                'total_annual_gross': total_annual_gross
            }

        except (TypeError, ValueError, InvalidOperation) as e:
            logger.error(f"Error calculating gross income: {str(e)}")
            raise ValueError(f"Error calculating gross income: {str(e)}")

    def calculate_pre_tax_deductions(self) -> Dict[str, Decimal]:
        """Calculate all pre-tax deductions"""
        deductions = {
            'retirement': Decimal('0'),
            'health_insurance': Decimal('0'),
            'fsa_hsa': Decimal('0'),
            'other_benefits': Decimal('0')
        }

        try:
            profile = self.budget.profile
            if profile:
                # Retirement
                if profile.retirement_contribution and profile.retirement_contribution > 0:
                    if profile.retirement_contribution_type == "pretax":
                        deductions['retirement'] = Decimal(str(profile.retirement_contribution))
                
                # Health Insurance
                if profile.health_insurance_premium and profile.health_insurance_premium > 0:
                    deductions['health_insurance'] = Decimal(str(profile.health_insurance_premium))
                
                # FSA/HSA
                fsa_hsa_total = (profile.hsa_contribution or 0) + (profile.fsa_contribution or 0)
                if fsa_hsa_total > 0:
                    deductions['fsa_hsa'] = Decimal(str(fsa_hsa_total))
                
                # Other benefits
                if profile.other_pretax_benefits and profile.other_pretax_benefits > 0:
                    deductions['other_benefits'] = Decimal(str(profile.other_pretax_benefits))

            deductions['total_deductions'] = sum(deductions.values())
            return deductions

        except (TypeError, ValueError, InvalidOperation) as e:
            logger.error(f"Error calculating pre-tax deductions: {str(e)}")
            raise ValueError(f"Error calculating pre-tax deductions: {str(e)}")

    def calculate_taxable_income(self) -> Dict[str, Decimal]:
        """Calculate taxable income after pre-tax deductions"""
        try:
            gross_income = self.calculate_gross_income()
            pre_tax_deductions = self.calculate_pre_tax_deductions()

            taxable_income = gross_income['total_annual_gross'] - pre_tax_deductions['total_deductions']

            if taxable_income < 0:
                logger.warning("Calculated taxable income is negative, setting to 0")
                taxable_income = Decimal('0')

            return {
                'gross_income': gross_income['total_annual_gross'],
                'pre_tax_deductions': pre_tax_deductions['total_deductions'],
                'taxable_income': taxable_income
            }

        except (TypeError, ValueError, InvalidOperation) as e:
            logger.error(f"Error calculating taxable income: {str(e)}")
            raise ValueError(f"Error calculating taxable income: {str(e)}")

    def calculate_tax_withholdings(self) -> Dict[str, Decimal]:
        """Calculate current tax withholdings using fixed rates"""
        logger.debug("Starting tax withholdings calculation")

        withholdings = {
            'federal': Decimal('0'),
            'state': Decimal('0'),
            'local': Decimal('0'),
            'fica': Decimal('0')
        }

        try:
            # Get taxable income first
            taxable_income_data = self.calculate_taxable_income()
            taxable_income = taxable_income_data['taxable_income']

            if taxable_income <= 0:
                logger.debug("No taxable income to calculate withholdings")
                withholdings['total_withholdings'] = Decimal('0')
                return withholdings

            profile = self.budget.profile
            if not profile:
                raise ValueError("Profile not found for tax calculation")

            # Federal Tax Calculation with basic brackets
            federal_tax = self._calculate_federal_tax(taxable_income)
            
            # State tax calculation
            state_tax = self._calculate_state_tax(taxable_income, profile.state)

            # FICA calculation (Social Security 6.2% up to limit + Medicare 1.45% no limit)
            fica_tax = self._calculate_fica_tax(taxable_income)

            # Add any additional withholding from profile
            if profile.federal_additional_withholding:
                federal_tax += Decimal(str(profile.federal_additional_withholding))
            if profile.state_additional_withholding:
                state_tax += Decimal(str(profile.state_additional_withholding))

            withholdings['federal'] = federal_tax
            withholdings['state'] = state_tax
            withholdings['fica'] = fica_tax
            withholdings['total_withholdings'] = sum(withholdings.values())

            return withholdings

        except Exception as e:
            logger.error(f"Error in calculate_tax_withholdings: {str(e)}")
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

    def calculate_budget(self):
        """Calculate the final budget including all income sources and tax withholdings."""
        try:
            # Validate inputs first
            if not self.budget.gross_income_sources:
                raise ValueError("No income sources found")
                
            # Get gross income details
            gross_income_data = self.calculate_gross_income()
            total_gross = gross_income_data['total_annual_gross']
            
            if total_gross <= 0:
                raise ValueError("Total gross income must be positive")
            
            # Get deductions
            deductions = self.calculate_pre_tax_deductions()
            
            # Get tax withholdings
            tax_data = self.calculate_tax_withholdings()
            
            # Calculate net income
            net_income = total_gross - deductions['total_deductions'] - tax_data['total_withholdings']
            
            # Return comprehensive budget breakdown
            return {
                'gross_income': {
                    'annual': total_gross,
                    'monthly': total_gross / Decimal('12'),
                    'biweekly': total_gross / Decimal('26')
                },
                'deductions': deductions,
                'taxes': tax_data,
                'net_income': {
                    'annual': net_income,
                    'monthly': net_income / Decimal('12'),
                    'biweekly': net_income / Decimal('26')
                }
            }
            
        except (InvalidOperation, DivisionByZero) as e:
            logger.error(f"Calculation error: {str(e)}")
            raise ValueError(f"Invalid calculation: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
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
