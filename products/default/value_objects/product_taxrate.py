from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass(frozen=True)
class TaxRate:
    value: Decimal
    
    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            raise ValueError("Tax rate must be a Decimal")
        if self.value < 0:
            raise ValueError("Tax rate cannot be negative")
        if self.value > 1:
            raise ValueError("Tax rate cannot exceed 1 (100%)")
        if self.value.as_tuple().exponent < -4:
            raise ValueError("Tax rate must have at most 4 decimal places")
    
    def __str__(self) -> str:
        return f"{self.value * 100:.2f}%"
    
    @classmethod
    def from_optional(cls, value: Optional[Decimal]) -> Optional['TaxRate']:
        if value is None:
            return None
        return cls(value)

if __name__ == "__main__":
    from decimal import Decimal
    
    # Valid tax rates
    tax1 = TaxRate(Decimal("0.08"))
    tax2 = TaxRate(Decimal("0.20"))
    print(tax1)  # 8.00%
    print(tax2)  # 20.00%
    
    # Test from_optional
    tax3 = TaxRate.from_optional(Decimal("0.10"))
    print(tax3)  # 10.00%
    
    tax4 = TaxRate.from_optional(None)
    print(tax4)  # None
    
    # These will raise ValueError
    try:
        tax5 = TaxRate(Decimal("-0.05"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Tax rate cannot be negative
    
    try:
        tax6 = TaxRate(Decimal("1.5"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Tax rate cannot exceed 1 (100%)
    
    try:
        tax7 = TaxRate(Decimal("0.12345"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Tax rate must have at most 4 decimal places
