from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ProductCategory:
    value: str
    
    def __post_init__(self):
        valid_categories = ['electronics', 'clothing', 'books', 'home', 'toys', 'food', 'beauty', 'sports', 'automotive', 'other']
        if self.value not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['ProductCategory']:
        if value is None:
            return None
        return cls(value)

if __name__ == "__main__":
    # Valid categories
    cat1 = ProductCategory("electronics")
    cat2 = ProductCategory("beauty")
    print(cat1)  # electronics
    print(cat2)  # beauty
    
    # Test from_optional
    cat3 = ProductCategory.from_optional("sports")
    print(cat3)  # sports
    
    cat4 = ProductCategory.from_optional(None)
    print(cat4)  # None
    
    # This will raise ValueError
    try:
        cat5 = ProductCategory("invalid")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Invalid category. Must be one of: electronics, clothing, books, home, toys, food, beauty, sports, automotive, other

