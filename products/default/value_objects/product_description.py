from dataclasses import dataclass

@dataclass(frozen=True)
class ProductDescription:
    value: str
    
    def __post_init__(self):
        cleaned = self.value.strip()
        if not cleaned or len(cleaned) < 10 or len(cleaned) > 5000:
            raise ValueError("Description must be 10-5000 characters")
        if any(c in cleaned for c in ['<', '>', '{', '}']):
            raise ValueError("Description contains invalid HTML/markup characters")
        object.__setattr__(self, 'value', ' '.join(cleaned.split()))
    
    def excerpt(self, length: int = 100) -> str:
        return self.value[:length] + ("..." if len(self.value) > length else "")
    
    def word_count(self) -> int:
        return len(self.value.split())
    
    def contains_keyword(self, keyword: str) -> bool:
        return keyword.lower() in self.value.lower()

if __name__ == "__main__":
    # Valid description
    desc1 = ProductDescription("This is a high-quality electronic device with excellent features and performance.")
    print(desc1.value)
    print(desc1.excerpt(20))  # This is a high-qua...
    print(desc1.word_count())  # 12
    print(desc1.contains_keyword("electronic"))  # True
    print(desc1.contains_keyword("battery"))  # False
    
    # Test auto-formatting (removes extra spaces)
    desc2 = ProductDescription("  This   is   a   test   description   ")
    print(desc2.value)  # This is a test description
    
    # Test longer description
    long_desc = " ".join(["word"] * 100)
    desc3 = ProductDescription(long_desc)
    print(desc3.word_count())  # 100
    
    # These will raise ValueError
    try:
        desc4 = ProductDescription("Short")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Description must be 10-5000 characters
    
    try:
        desc5 = ProductDescription("This contains <html> tags")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Description contains invalid HTML/markup characters
    
    try:
        desc6 = ProductDescription("A" * 5001)
    except ValueError as e:
        print(f"Error: {e}")  # Error: Description must be 10-5000 characters
    