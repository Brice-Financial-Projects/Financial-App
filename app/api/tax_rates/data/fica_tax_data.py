"""FICA tax data for various tax years."""
from typing import Dict, Optional
from ..models import FICATaxData

# FICA Tax Data by Year
FICA_TAX_DATA = {
    2024: FICATaxData(
        year=2024,
        social_security_rate=0.062,  # 6.2%
        medicare_rate=0.0145,  # 1.45%
        additional_medicare_rate=0.009,  # 0.9%
        social_security_wage_base=168600,  # For 2024
        additional_medicare_threshold=200000  # Single threshold
    ),
    2023: FICATaxData(
        year=2023,
        social_security_rate=0.062,  # 6.2%
        medicare_rate=0.0145,  # 1.45%
        additional_medicare_rate=0.009,  # 0.9%
        social_security_wage_base=160200,  # For 2023
        additional_medicare_threshold=200000  # Single threshold
    )
}

def get_fica_rates(year: int) -> Optional[FICATaxData]:
    """Get FICA tax rates for a specific year."""
    return FICA_TAX_DATA.get(year)

def get_available_years() -> list[int]:
    """Get list of available tax years."""
    return sorted(FICA_TAX_DATA.keys())

def calculate_fica_tax(income: float, year: int) -> Dict[str, float]:
    """Calculate FICA taxes (Social Security and Medicare) for given income and year."""
    tax_data = FICA_TAX_DATA.get(year)
    if not tax_data:
        raise ValueError(f"FICA tax data not available for year {year}")
    
    # Calculate Social Security tax
    social_security_tax = min(income, tax_data.social_security_wage_base) * tax_data.social_security_rate
    
    # Calculate Medicare tax
    medicare_tax = income * tax_data.medicare_rate
    
    # Calculate Additional Medicare Tax if applicable
    if income > tax_data.additional_medicare_threshold:
        additional_medicare_tax = (income - tax_data.additional_medicare_threshold) * tax_data.additional_medicare_rate
        medicare_tax += additional_medicare_tax
    
    return {
        'social_security': round(social_security_tax, 2),
        'medicare': round(medicare_tax, 2),
        'total': round(social_security_tax + medicare_tax, 2)
    } 