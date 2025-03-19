"""State tax data for various tax years."""
from typing import Dict, List, Optional
from ..models import TaxBracket, StateTaxData

# 2024 State Tax Brackets
STATE_TAX_BRACKETS_2024 = {
    'CA': [  # California - Progressive
        TaxBracket(0.01, 0, 10099),
        TaxBracket(0.02, 10099, 23942),
        TaxBracket(0.04, 23942, 37788),
        TaxBracket(0.06, 37788, 52455),
        TaxBracket(0.08, 52455, 66295),
        TaxBracket(0.093, 66295, 338639),
        TaxBracket(0.103, 338639, 406364),
        TaxBracket(0.113, 406364, 677275),
        TaxBracket(0.123, 677275, None)
    ],
    'NY': [  # New York - Progressive
        TaxBracket(0.04, 0, 8500),
        TaxBracket(0.045, 8500, 11700),
        TaxBracket(0.0525, 11700, 13900),
        TaxBracket(0.059, 13900, 80650),
        TaxBracket(0.0597, 80650, 215400),
        TaxBracket(0.0633, 215400, 1077550),
        TaxBracket(0.0685, 1077550, 5000000),
        TaxBracket(0.0965, 5000000, 25000000),
        TaxBracket(0.103, 25000000, None)
    ],
    'TX': [  # Texas - No state income tax
        TaxBracket(0.0, 0, None)
    ],
    'FL': [  # Florida - No state income tax
        TaxBracket(0.0, 0, None)
    ],
    'WA': [  # Washington - No state income tax
        TaxBracket(0.0, 0, None)
    ],
    'IL': [  # Illinois - Flat tax
        TaxBracket(0.0495, 0, None)
    ]
}

# 2023 State Tax Brackets (same as 2024 for example purposes)
STATE_TAX_BRACKETS_2023 = STATE_TAX_BRACKETS_2024.copy()

# Standard Deductions by State (2024)
STATE_STANDARD_DEDUCTIONS_2024 = {
    'CA': {
        'single': 5202,
        'married_joint': 10404,
        'married_separate': 5202,
        'head_household': 10404
    },
    'NY': {
        'single': 8000,
        'married_joint': 16050,
        'married_separate': 8000,
        'head_household': 11200
    }
}

# Standard Deductions by State (2023)
STATE_STANDARD_DEDUCTIONS_2023 = STATE_STANDARD_DEDUCTIONS_2024.copy()

# States with no income tax
NO_INCOME_TAX_STATES = {'TX', 'FL', 'WA', 'NV', 'AK', 'SD', 'WY', 'TN', 'NH'}

# Tax Data by State and Year
TAX_DATA = {}

# Initialize tax data for each year
for year in [2023, 2024]:
    TAX_DATA[year] = {}
    brackets = STATE_TAX_BRACKETS_2024 if year == 2024 else STATE_TAX_BRACKETS_2023
    deductions = STATE_STANDARD_DEDUCTIONS_2024 if year == 2024 else STATE_STANDARD_DEDUCTIONS_2023
    
    for state in brackets:
        has_state_tax = state not in NO_INCOME_TAX_STATES
        TAX_DATA[year][state] = StateTaxData(
            state=state,
            year=year,
            brackets=brackets[state],
            has_state_tax=has_state_tax,
            standard_deduction=deductions.get(state)
        )

def get_state_tax_brackets(state: str, year: int) -> Optional[List[TaxBracket]]:
    """Get state tax brackets for a specific state and year."""
    tax_data = TAX_DATA.get(year, {}).get(state.upper())
    return tax_data.brackets if tax_data else None

def get_state_standard_deduction(state: str, year: int) -> Optional[Dict[str, float]]:
    """Get state standard deduction for a specific state and year."""
    tax_data = TAX_DATA.get(year, {}).get(state.upper())
    return tax_data.standard_deduction if tax_data else None

def get_available_states() -> List[str]:
    """Get list of available states."""
    return sorted(STATE_TAX_BRACKETS_2024.keys())

def has_state_income_tax(state: str) -> bool:
    """Check if a state has income tax."""
    return state.upper() not in NO_INCOME_TAX_STATES

def calculate_tax(income: float, state: str, year: int, filing_status: str) -> float:
    """Calculate state tax for given income, state, year, and filing status."""
    tax_data = TAX_DATA.get(year, {}).get(state.upper())
    if not tax_data:
        raise ValueError(f"Tax data not available for state {state} and year {year}")
    
    if not tax_data.has_state_tax:
        return 0.0
        
    # Apply standard deduction if available
    if tax_data.standard_deduction and filing_status in tax_data.standard_deduction:
        income = max(0, income - tax_data.standard_deduction[filing_status])
    
    total_tax = 0
    for bracket in tax_data.brackets:
        if income <= 0:
            break
            
        if bracket.max_income is None:
            # Top bracket
            bracket_income = income
        else:
            bracket_income = min(income, bracket.max_income - bracket.min_income)
        
        total_tax += bracket_income * bracket.rate
        income -= bracket_income
    
    return round(total_tax, 2) 