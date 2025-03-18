"""Sample FICA tax data for testing and fallback."""

from typing import Dict, Any

# FICA tax data by year
FICA_TAX_DATA = {
    2022: {
        "year": 2022,
        "social_security_rate": 0.062,  # 6.2%
        "social_security_wage_base": 147000.0,
        "medicare_rate": 0.0145,  # 1.45%
        "additional_medicare_rate": 0.009,  # 0.9%
        "additional_medicare_threshold": 200000.0  # Single threshold
    },
    2023: {
        "year": 2023,
        "social_security_rate": 0.062,  # 6.2%
        "social_security_wage_base": 160200.0,
        "medicare_rate": 0.0145,  # 1.45%
        "additional_medicare_rate": 0.009,  # 0.9%
        "additional_medicare_threshold": 200000.0  # Single threshold
    },
    2024: {
        "year": 2024,
        "social_security_rate": 0.062,  # 6.2%
        "social_security_wage_base": 168600.0,  # Estimated 2024 wage base
        "medicare_rate": 0.0145,  # 1.45%
        "additional_medicare_rate": 0.009,  # 0.9%
        "additional_medicare_threshold": 200000.0  # Single threshold
    }
}


def get_fica_data(year: int) -> Dict[str, Any]:
    """
    Get FICA tax data for the given year.
    
    Args:
        year: Tax year
        
    Returns:
        Dictionary with FICA tax data
    """
    # Use most recent year if requested year is not available
    if year not in FICA_TAX_DATA:
        available_years = sorted(FICA_TAX_DATA.keys())
        year = available_years[-1]
    
    return FICA_TAX_DATA[year] 