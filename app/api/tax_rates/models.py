"""Models for tax rate API data structures."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class TaxBracket:
    """Tax bracket information."""
    min_income: float
    max_income: Optional[float]  # None for highest bracket
    rate: float  # Rate as decimal (e.g., 0.25 for 25%)
    

@dataclass
class FederalTaxData:
    """Federal tax rate data structure."""
    year: int
    brackets: List[TaxBracket]
    standard_deduction: float
    
    def get_rate_for_income(self, income: float) -> float:
        """Get the marginal tax rate for a given income level."""
        for bracket in self.brackets:
            if bracket.max_income is None or income <= bracket.max_income:
                return bracket.rate
        # Should never reach here
        return self.brackets[-1].rate


@dataclass
class StateTaxData:
    """State tax rate data structure."""
    state: str
    year: int
    brackets: List[TaxBracket]
    has_flat_tax: bool = False
    flat_tax_rate: float = 0.0
    
    def get_rate_for_income(self, income: float) -> float:
        """Get the marginal tax rate for a given income level."""
        if self.has_flat_tax:
            return self.flat_tax_rate
            
        for bracket in self.brackets:
            if bracket.max_income is None or income <= bracket.max_income:
                return bracket.rate
        # Should never reach here
        return self.brackets[-1].rate


@dataclass
class FICATaxData:
    """FICA tax data structure."""
    year: int
    social_security_rate: float
    social_security_wage_base: float
    medicare_rate: float
    additional_medicare_rate: float = 0.009  # 0.9% additional Medicare tax
    additional_medicare_threshold: float = 200000.0
    

@dataclass
class TaxCalculationRequest:
    """Request model for tax calculation."""
    income: float
    income_type: str  # "W2", "Self-Employed", "Other"
    state: str  # Two-letter state code
    year: int = field(default_factory=lambda: datetime.now().year)
    filing_status: str = "single"  # "single", "married_joint", "married_separate", "head_of_household"
    

@dataclass
class TaxCalculationResponse:
    """Response model for tax calculation."""
    income: float
    federal_tax: float
    state_tax: float
    fica_tax: float
    net_income: float
    effective_tax_rate: float
    marginal_federal_rate: float
    marginal_state_rate: float
    
    # Additional details
    federal_brackets: List[TaxBracket]
    state_brackets: List[TaxBracket]
    calculation_date: datetime = field(default_factory=datetime.now)
    
    @property
    def total_tax(self) -> float:
        """Total tax amount."""
        return self.federal_tax + self.state_tax + self.fica_tax 