"""Sample federal tax bracket data for testing and fallback."""

from typing import Dict, List, Any

# 2023 tax bracket data
FEDERAL_TAX_DATA_2023 = {
    "single": {
        "year": 2023,
        "brackets": [
            {"min_income": 0, "max_income": 11000, "rate": 0.10},
            {"min_income": 11000, "max_income": 44725, "rate": 0.12},
            {"min_income": 44725, "max_income": 95375, "rate": 0.22},
            {"min_income": 95375, "max_income": 182100, "rate": 0.24},
            {"min_income": 182100, "max_income": 231250, "rate": 0.32},
            {"min_income": 231250, "max_income": 578125, "rate": 0.35},
            {"min_income": 578125, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 13850.0
    },
    "married_joint": {
        "year": 2023,
        "brackets": [
            {"min_income": 0, "max_income": 22000, "rate": 0.10},
            {"min_income": 22000, "max_income": 89450, "rate": 0.12},
            {"min_income": 89450, "max_income": 190750, "rate": 0.22},
            {"min_income": 190750, "max_income": 364200, "rate": 0.24},
            {"min_income": 364200, "max_income": 462500, "rate": 0.32},
            {"min_income": 462500, "max_income": 693750, "rate": 0.35},
            {"min_income": 693750, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 27700.0
    },
    "married_separate": {
        "year": 2023,
        "brackets": [
            {"min_income": 0, "max_income": 11000, "rate": 0.10},
            {"min_income": 11000, "max_income": 44725, "rate": 0.12},
            {"min_income": 44725, "max_income": 95375, "rate": 0.22},
            {"min_income": 95375, "max_income": 182100, "rate": 0.24},
            {"min_income": 182100, "max_income": 231250, "rate": 0.32},
            {"min_income": 231250, "max_income": 346875, "rate": 0.35},
            {"min_income": 346875, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 13850.0
    },
    "head_of_household": {
        "year": 2023,
        "brackets": [
            {"min_income": 0, "max_income": 15700, "rate": 0.10},
            {"min_income": 15700, "max_income": 59850, "rate": 0.12},
            {"min_income": 59850, "max_income": 95350, "rate": 0.22},
            {"min_income": 95350, "max_income": 182100, "rate": 0.24},
            {"min_income": 182100, "max_income": 231250, "rate": 0.32},
            {"min_income": 231250, "max_income": 578100, "rate": 0.35},
            {"min_income": 578100, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 20800.0
    }
}

# 2024 tax bracket data (projected)
FEDERAL_TAX_DATA_2024 = {
    "single": {
        "year": 2024,
        "brackets": [
            {"min_income": 0, "max_income": 11600, "rate": 0.10},
            {"min_income": 11600, "max_income": 47150, "rate": 0.12},
            {"min_income": 47150, "max_income": 100525, "rate": 0.22},
            {"min_income": 100525, "max_income": 191950, "rate": 0.24},
            {"min_income": 191950, "max_income": 243725, "rate": 0.32},
            {"min_income": 243725, "max_income": 609350, "rate": 0.35},
            {"min_income": 609350, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 14600.0
    },
    "married_joint": {
        "year": 2024,
        "brackets": [
            {"min_income": 0, "max_income": 23200, "rate": 0.10},
            {"min_income": 23200, "max_income": 94300, "rate": 0.12},
            {"min_income": 94300, "max_income": 201050, "rate": 0.22},
            {"min_income": 201050, "max_income": 383900, "rate": 0.24},
            {"min_income": 383900, "max_income": 487450, "rate": 0.32},
            {"min_income": 487450, "max_income": 731200, "rate": 0.35},
            {"min_income": 731200, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 29200.0
    },
    "married_separate": {
        "year": 2024,
        "brackets": [
            {"min_income": 0, "max_income": 11600, "rate": 0.10},
            {"min_income": 11600, "max_income": 47150, "rate": 0.12},
            {"min_income": 47150, "max_income": 100525, "rate": 0.22},
            {"min_income": 100525, "max_income": 191950, "rate": 0.24},
            {"min_income": 191950, "max_income": 243725, "rate": 0.32},
            {"min_income": 243725, "max_income": 365600, "rate": 0.35},
            {"min_income": 365600, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 14600.0
    },
    "head_of_household": {
        "year": 2024,
        "brackets": [
            {"min_income": 0, "max_income": 16550, "rate": 0.10},
            {"min_income": 16550, "max_income": 63100, "rate": 0.12},
            {"min_income": 63100, "max_income": 100500, "rate": 0.22},
            {"min_income": 100500, "max_income": 191950, "rate": 0.24},
            {"min_income": 191950, "max_income": 243700, "rate": 0.32},
            {"min_income": 243700, "max_income": 609350, "rate": 0.35},
            {"min_income": 609350, "max_income": None, "rate": 0.37}
        ],
        "standard_deduction": 21900.0
    }
}

# Collection of all years
FEDERAL_TAX_DATA: Dict[int, Dict[str, Any]] = {
    2023: FEDERAL_TAX_DATA_2023,
    2024: FEDERAL_TAX_DATA_2024
}


def get_federal_tax_data(year: int, filing_status: str = "single") -> Dict[str, Any]:
    """
    Get federal tax data for the given year and filing status.
    
    Args:
        year: Tax year
        filing_status: Filing status (single, married_joint, etc.)
        
    Returns:
        Dictionary with tax bracket data
    """
    # Use most recent year if requested year is not available
    if year not in FEDERAL_TAX_DATA:
        available_years = sorted(FEDERAL_TAX_DATA.keys())
        year = available_years[-1]
    
    # Use single filing status if requested status is not available
    if filing_status not in FEDERAL_TAX_DATA[year]:
        filing_status = "single"
    
    return FEDERAL_TAX_DATA[year][filing_status] 