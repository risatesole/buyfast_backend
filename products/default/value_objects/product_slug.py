from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class Slug:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Slug cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Slug cannot exceed 255 characters")
        cleaned = self.value.strip().lower()
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', cleaned):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        object.__setattr__(self, 'value', cleaned)

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['Slug']:
        if value is None or not value.strip():
            return None
        return cls(value)

if __name__ == "__main__":
    # Valid slugs
    slug1 = Slug("electronics")
    slug2 = Slug("new-product-2024")
    print(slug1)  # electronics
    print(slug2)  # new-product-2024

    # Auto-lowercase
    slug3 = Slug("Books-And-More")
    print(slug3)  # books-and-more

    # Test from_optional
    slug4 = Slug.from_optional("gadget-sale")
    print(slug4)  # gadget-sale

    slug5 = Slug.from_optional(None)
    print(slug5)  # None

    # These will raise ValueError
    try:
        slug6 = Slug("")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Slug cannot be empty

    try:
        slug7 = Slug("invalid slug")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Slug must contain only lowercase letters, numbers, and hyphens

    try:
        slug8 = Slug("-invalid-start")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Slug must contain only lowercase letters, numbers, and hyphens
