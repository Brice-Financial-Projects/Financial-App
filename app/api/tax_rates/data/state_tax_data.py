"""Sample state tax bracket data for testing and fallback."""

from typing import Dict, List, Any

# 2023 sample state tax data
STATE_TAX_DATA_2023 = {
    "CA": {  # California - progressive tax rates
        "single": {
            "year": 2023,
            "state": "CA",
            "has_flat_tax": False,
            "flat_tax_rate": 0.0,
            "brackets": [
                {"min_income": 0, "max_income": 10099, "rate": 0.01},
                {"min_income": 10099, "max_income": 23942, "rate": 0.02},
                {"min_income": 23942, "max_income": 37788, "rate": 0.04},
                {"min_income": 37788, "max_income": 52455, "rate": 0.06},
                {"min_income": 52455, "max_income": 66295, "rate": 0.08},
                {"min_income": 66295, "max_income": 338639, "rate": 0.093},
                {"min_income": 338639, "max_income": 406364, "rate": 0.103},
                {"min_income": 406364, "max_income": 677275, "rate": 0.113},
                {"min_income": 677275, "max_income": None, "rate": 0.123}
            ]
        },
        "married_joint": {
            "year": 2023,
            "state": "CA",
            "has_flat_tax": False,
            "flat_tax_rate": 0.0,
            "brackets": [
                {"min_income": 0, "max_income": 20198, "rate": 0.01},
                {"min_income": 20198, "max_income": 47884, "rate": 0.02},
                {"min_income": 47884, "max_income": 75576, "rate": 0.04},
                {"min_income": 75576, "max_income": 104910, "rate": 0.06},
                {"min_income": 104910, "max_income": 132590, "rate": 0.08},
                {"min_income": 132590, "max_income": 677278, "rate": 0.093},
                {"min_income": 677278, "max_income": 812728, "rate": 0.103},
                {"min_income": 812728, "max_income": 1354550, "rate": 0.113},
                {"min_income": 1354550, "max_income": None, "rate": 0.123}
            ]
        }
    },
    "TX": {  # Texas - no state income tax
        "single": {
            "year": 2023,
            "state": "TX",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0,
            "brackets": []
        },
        "married_joint": {
            "year": 2023,
            "state": "TX",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0,
            "brackets": []
        }
    },
    "IL": {  # Illinois - flat tax
        "single": {
            "year": 2023,
            "state": "IL",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0495,
            "brackets": []
        },
        "married_joint": {
            "year": 2023,
            "state": "IL",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0495,
            "brackets": []
        }
    },
    "NY": {  # New York - progressive tax rates
        "single": {
            "year": 2023,
            "state": "NY",
            "has_flat_tax": False,
            "flat_tax_rate": 0.0,
            "brackets": [
                {"min_income": 0, "max_income": 13900, "rate": 0.04},
                {"min_income": 13900, "max_income": 21400, "rate": 0.045},
                {"min_income": 21400, "max_income": 80650, "rate": 0.0525},
                {"min_income": 80650, "max_income": 215400, "rate": 0.0585},
                {"min_income": 215400, "max_income": 1077550, "rate": 0.0625},
                {"min_income": 1077550, "max_income": 5000000, "rate": 0.0685},
                {"min_income": 5000000, "max_income": 25000000, "rate": 0.0965},
                {"min_income": 25000000, "max_income": None, "rate": 0.1090}
            ]
        },
        "married_joint": {
            "year": 2023,
            "state": "NY",
            "has_flat_tax": False,
            "flat_tax_rate": 0.0,
            "brackets": [
                {"min_income": 0, "max_income": 27900, "rate": 0.04},
                {"min_income": 27900, "max_income": 42800, "rate": 0.045},
                {"min_income": 42800, "max_income": 161550, "rate": 0.0525},
                {"min_income": 161550, "max_income": 323200, "rate": 0.0585},
                {"min_income": 323200, "max_income": 2155350, "rate": 0.0625},
                {"min_income": 2155350, "max_income": 5000000, "rate": 0.0685},
                {"min_income": 5000000, "max_income": 25000000, "rate": 0.0965},
                {"min_income": 25000000, "max_income": None, "rate": 0.1090}
            ]
        }
    },
    "FL": {  # Florida - no state income tax
        "single": {
            "year": 2023,
            "state": "FL",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0,
            "brackets": []
        },
        "married_joint": {
            "year": 2023,
            "state": "FL",
            "has_flat_tax": True,
            "flat_tax_rate": 0.0,
            "brackets": []
        }
    },
}

# 2024 sample state tax data (using 2023 values as placeholders)
STATE_TAX_DATA_2024 = STATE_TAX_DATA_2023.copy()
for state in STATE_TAX_DATA_2024:
    for filing_status in STATE_TAX_DATA_2024[state]:
        STATE_TAX_DATA_2024[state][filing_status]["year"] = 2024

# Collection of all years
STATE_TAX_DATA: Dict[int, Dict[str, Dict[str, Any]]] = {
    2023: STATE_TAX_DATA_2023,
    2024: STATE_TAX_DATA_2024
}

# Default state data for states not in our database
DEFAULT_STATE_DATA = {
    "year": 2023,
    "state": "XX",
    "has_flat_tax": True,
    "flat_tax_rate": 0.05,  # 5% default flat tax rate
    "brackets": []
}


def get_state_tax_data(state: str, year: int, filing_status: str = "single") -> Dict[str, Any]:
    """
    Get state tax data for the given state, year, and filing status.
    
    Args:
        state: Two-letter state code
        year: Tax year
        filing_status: Filing status (single, married_joint, etc.)
        
    Returns:
        Dictionary with state tax bracket data
    """
    # Use most recent year if requested year is not available
    if year not in STATE_TAX_DATA:
        available_years = sorted(STATE_TAX_DATA.keys())
        year = available_years[-1]
    
    # Use default data if state is not available
    if state not in STATE_TAX_DATA[year]:
        result = DEFAULT_STATE_DATA.copy()
        result["year"] = year
        result["state"] = state
        return result
    
    # Use single filing status if requested status is not available
    if filing_status not in STATE_TAX_DATA[year][state]:
        filing_status = "single"
    
    return STATE_TAX_DATA[year][state][filing_status] 