from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ProductType:
    value: str
    
    def __post_init__(self):
        valid_types = ['normal','electronics', 'clothing', 'books', 'home', 'toys', 'food', 'other']
        if self.value not in valid_types:
            raise ValueError(f"Invalid variant. Must be one of: {', '.join(valid_types)}")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['ProductType']:
        if value is None:
            return None
        return cls(value)

if __name__ == "__main__":
    # Valid variants
    variant1 = ProductType("electronics")
    variant2 = ProductType("books")
    print(variant1)  # electronics
    print(variant2)  # books
    
    # Test from_optional
    variant3 = ProductType.from_optional("clothing")
    print(variant3)  # clothing
    
    variant4 = ProductType.from_optional(None)
    print(variant4)  # None
    
    # This will raise ValueError
    try:
        variant5 = ProductType("invalid")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Invalid variant. Must be one of: electronics, clothing, books, home, toys, food, other
