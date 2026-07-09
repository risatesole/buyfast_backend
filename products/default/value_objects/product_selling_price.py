from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass(frozen=True)
class SellingPrice:
    value: Decimal
    
    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            raise ValueError("Price must be a Decimal")
        if self.value < 0:
            raise ValueError("Price cannot be negative")
        if self.value > 999999.99:
            raise ValueError("Price cannot exceed 999999.99")
        if self.value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most 2 decimal places")
    
    def __str__(self) -> str:
        return f"${self.value:.2f}"
    
    @classmethod
    def from_optional(cls, value: Optional[Decimal]) -> Optional['SellingPrice']:
        if value is None:
            return None
        return cls(value)

if __name__ == "__main__":
    from decimal import Decimal
    
    # Valid prices
    price1 = SellingPrice(Decimal("19.99"))
    price2 = SellingPrice(Decimal("100.00"))
    print(price1)  # $19.99
    print(price2)  # $100.00
    
    # Test from_optional
    price3 = SellingPrice.from_optional(Decimal("49.50"))
    print(price3)  # $49.50
    
    price4 = SellingPrice.from_optional(None)
    print(price4)  # None
    
    # These will raise ValueError
    try:
        price5 = SellingPrice(Decimal("-5.00"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Price cannot be negative
    
    try:
        price6 = SellingPrice(Decimal("19.999"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Price must have at most 2 decimal places
    
    try:
        price7 = SellingPrice(Decimal("1000000.00"))
    except ValueError as e:
        print(f"Error: {e}")  # Error: Price cannot exceed 999999.99
