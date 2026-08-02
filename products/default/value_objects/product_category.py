from typing import Optional


class ProductCategory:
    """
    Wraps the category slug for a product. Categories themselves are no longer
    a fixed set of Python values - they're rows in the Category table - so this
    just validates that a slug string was provided; whether it corresponds to a
    real category is checked against the database (e.g. by the repository).
    """

    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("category is required and must be a non-empty string")
        self.value = value.strip().lower()

    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['ProductCategory']:
        if value is None:
            return None
        return cls(value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        return isinstance(other, ProductCategory) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
