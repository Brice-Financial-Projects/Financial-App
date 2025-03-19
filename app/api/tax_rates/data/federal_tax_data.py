"""Federal tax data for various tax years."""
from typing import List, Dict, Optional
from ..models import TaxBracket, FederalTaxData

# 2024 Tax Brackets
FEDERAL_TAX_BRACKETS_2024 = {
    'single': [
        TaxBracket(0.10, 0, 11600),
        TaxBracket(0.12, 11600, 47150),
        TaxBracket(0.22, 47150, 100525),
        TaxBracket(0.24, 100525, 191950),
        TaxBracket(0.32, 191950, 243725),
        TaxBracket(0.35, 243725, 609350),
        TaxBracket(0.37, 609350, None)
    ],
    'married_joint': [
        TaxBracket(0.10, 0, 23200),
        TaxBracket(0.12, 23200, 94300),
        TaxBracket(0.22, 94300, 201050),
        TaxBracket(0.24, 201050, 383900),
        TaxBracket(0.32, 383900, 487450),
        TaxBracket(0.35, 487450, 731200),
        TaxBracket(0.37, 731200, None)
    ],
    'married_separate': [
        TaxBracket(0.10, 0, 11600),
        TaxBracket(0.12, 11600, 47150),
        TaxBracket(0.22, 47150, 100525),
        TaxBracket(0.24, 100525, 191950),
        TaxBracket(0.32, 191950, 243725),
        TaxBracket(0.35, 243725, 365600),
        TaxBracket(0.37, 365600, None)
    ],
    'head_household': [
        TaxBracket(0.10, 0, 16550),
        TaxBracket(0.12, 16550, 63100),
        TaxBracket(0.22, 63100, 100500),
        TaxBracket(0.24, 100500, 191950),
        TaxBracket(0.32, 191950, 243700),
        TaxBracket(0.35, 243700, 609350),
        TaxBracket(0.37, 609350, None)
    ]
}

# 2023 Tax Brackets
FEDERAL_TAX_BRACKETS_2023 = {
    'single': [
        TaxBracket(0.10, 0, 11000),
        TaxBracket(0.12, 11000, 44725),
        TaxBracket(0.22, 44725, 95375),
        TaxBracket(0.24, 95375, 182100),
        TaxBracket(0.32, 182100, 231250),
        TaxBracket(0.35, 231250, 578125),
        TaxBracket(0.37, 578125, None)
    ],
    'married_joint': [
        TaxBracket(0.10, 0, 22000),
        TaxBracket(0.12, 22000, 89450),
        TaxBracket(0.22, 89450, 190750),
        TaxBracket(0.24, 190750, 364200),
        TaxBracket(0.32, 364200, 462500),
        TaxBracket(0.35, 462500, 693750),
        TaxBracket(0.37, 693750, None)
    ],
    'married_separate': [
        TaxBracket(0.10, 0, 11000),
        TaxBracket(0.12, 11000, 44725),
        TaxBracket(0.22, 44725, 95375),
        TaxBracket(0.24, 95375, 182100),
        TaxBracket(0.32, 182100, 231250),
        TaxBracket(0.35, 231250, 346875),
        TaxBracket(0.37, 346875, None)
    ],
    'head_household': [
        TaxBracket(0.10, 0, 15700),
        TaxBracket(0.12, 15700, 59850),
        TaxBracket(0.22, 59850, 95350),
        TaxBracket(0.24, 95350, 182100),
        TaxBracket(0.32, 182100, 231250),
        TaxBracket(0.35, 231250, 578100),
        TaxBracket(0.37, 578100, None)
    ]
}

# Standard Deductions
STANDARD_DEDUCTIONS = {
    2024: {
        'single': 14600,
        'married_joint': 29200,
        'married_separate': 14600,
        'head_household': 21900
    },
    2023: {
        'single': 13850,
        'married_joint': 27700,
        'married_separate': 13850,
        'head_household': 20800
    }
}

# Tax Data by Year
TAX_DATA = {
    2024: FederalTaxData(
        year=2024,
        brackets=FEDERAL_TAX_BRACKETS_2024,
        standard_deduction=STANDARD_DEDUCTIONS[2024]
    ),
    2023: FederalTaxData(
        year=2023,
        brackets=FEDERAL_TAX_BRACKETS_2023,
        standard_deduction=STANDARD_DEDUCTIONS[2023]
    )
}

def get_federal_tax_brackets(year: int) -> Optional[Dict[str, List[TaxBracket]]]:
    """Get federal tax brackets for a specific year."""
    tax_data = TAX_DATA.get(year)
    return tax_data.brackets if tax_data else None

def get_standard_deduction(year: int) -> Optional[Dict[str, float]]:
    """Get standard deduction amounts for a specific year."""
    return STANDARD_DEDUCTIONS.get(year)

def get_available_years() -> List[int]:
    """Get list of available tax years."""
    return sorted(TAX_DATA.keys())

def calculate_tax(income: float, year: int, filing_status: str) -> float:
    """Calculate federal tax for given income, year, and filing status."""
    tax_data = TAX_DATA.get(year)
    if not tax_data or filing_status not in tax_data.brackets:
        raise ValueError(f"Tax data not available for year {year} and filing status {filing_status}")

    brackets = tax_data.brackets[filing_status]
    standard_deduction = tax_data.standard_deduction[filing_status]
    
    # Apply standard deduction
    taxable_income = max(0, income - standard_deduction)
    
    total_tax = 0
    for bracket in brackets:
        if taxable_income <= 0:
            break
            
        if bracket.max_income is None:
            # Top bracket
            bracket_income = taxable_income
        else:
            bracket_income = min(taxable_income, bracket.max_income - bracket.min_income)
        
        total_tax += bracket_income * bracket.rate
        taxable_income -= bracket_income
    
    return round(total_tax, 2) 