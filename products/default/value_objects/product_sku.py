from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class SKU:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("SKU cannot be empty")
        if len(self.value) > 50:
            raise ValueError("SKU cannot exceed 50 characters")
        cleaned = self.value.strip().upper()
        if not re.match(r'^[A-Z0-9\-]+$', cleaned):
            raise ValueError("SKU must contain only uppercase letters, numbers, and hyphens")
        object.__setattr__(self, 'value', cleaned)

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['SKU']:
        if value is None or not value.strip():
            return None
        return cls(value)

if __name__ == "__main__":
    # Valid SKUs
    sku1 = SKU("ABC-123")
    sku2 = SKU("XYZ-456-DEF")
    print(sku1)  # ABC-123
    print(sku2)  # XYZ-456-DEF

    # Auto-uppercase
    sku3 = SKU("abc-789")
    print(sku3)  # ABC-789

    # Test from_optional
    sku4 = SKU.from_optional("TEST-001")
    print(sku4)  # TEST-001

    sku5 = SKU.from_optional(None)
    print(sku5)  # None

    # These will raise ValueError
    try:
        sku6 = SKU("")
    except ValueError as e:
        print(f"Error: {e}")  # Error: SKU cannot be empty

    try:
        sku7 = SKU("abc def")
    except ValueError as e:
        print(f"Error: {e}")  # Error: SKU must contain only uppercase letters, numbers, and hyphens
