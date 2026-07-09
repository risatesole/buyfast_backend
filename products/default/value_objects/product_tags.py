from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class Tags:
    value: List[str]

    def __post_init__(self):
        if not isinstance(self.value, list):
            raise ValueError("Tags must be a list")
        if len(self.value) > 10:
            raise ValueError("Cannot have more than 10 tags")
        cleaned = [tag.strip().lower() for tag in self.value if tag and tag.strip()]
        if len(cleaned) != len(self.value):
            raise ValueError("Tags cannot be empty strings")
        for tag in cleaned:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 characters")
            if not all(c.isalnum() or c in ['-', '_'] for c in tag):
                raise ValueError(f"Tag '{tag}' contains invalid characters")
        object.__setattr__(self, 'value', cleaned)

    def __str__(self) -> str:
        return ', '.join(self.value)

    @classmethod
    def from_optional(cls, value: Optional[List[str]]) -> Optional['Tags']:
        if value is None:
            return None
        return cls(value)

if __name__ == "__main__":
    # Valid tags
    tags1 = Tags(["electronics", "gadget", "new"])
    tags2 = Tags(["python", "django", "web", "api"])
    print(tags1)  # electronics, gadget, new
    print(tags2)  # python, django, web, api

    # Test from_optional
    tags3 = Tags.from_optional(["sale", "discount"])
    print(tags3)  # sale, discount

    tags4 = Tags.from_optional(None)
    print(tags4)  # None

    # These will raise ValueError
    try:
        tags5 = Tags(["", "valid"])
    except ValueError as e:
        print(f"Error: {e}")  # Error: Tags cannot be empty strings

    try:
        tags6 = Tags(["tag with spaces"])
    except ValueError as e:
        print(f"Error: {e}")  # Error: Tag 'tag with spaces' contains invalid characters
