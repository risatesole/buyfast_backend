from dataclasses import dataclass

@dataclass(frozen=True)
class ProductName:
    value: str
    
    def __post_init__(self):
        cleaned = self.value.strip()
        if not cleaned or len(cleaned) < 3 or len(cleaned) > 100:
            raise ValueError("Product name must be 3-100 characters")
        if not all(c.isalnum() or c.isspace() or c in "-_,.&'()!" for c in cleaned):
            raise ValueError("Product name contains invalid characters")
        object.__setattr__(self, 'value', ' '.join(cleaned.split()).title())
    
    def contains(self, term: str) -> bool:
        return term.lower() in self.value.lower()
    
    def to_slug(self) -> str:
        return ''.join(c if c.isalnum() else '-' for c in self.value.lower()).strip('-')

if __name__ == "__main__":
    # Valid product names
    name1 = ProductName("Apple iPhone 15 Pro")
    name2 = ProductName("Sony WH-1000XM4 Headphones")
    name3 = ProductName("Dell XPS 13 Laptop")
    print(name1)  # Apple Iphone 15 Pro (dataclass repr)
    print(name1.value)  # Apple Iphone 15 Pro
    print(name2.value)  # Sony Wh-1000Xm4 Headphones
    print(name3.value)  # Dell Xps 13 Laptop
    
    # Test contains method
    print(name1.contains("iphone"))  # True
    print(name1.contains("samsung"))  # False
    
    # Test to_slug method
    print(name1.to_slug())  # apple-iphone-15-pro
    print(name2.to_slug())  # sony-wh-1000xm4-headphones
    
    # Test auto-formatting (removes extra spaces, title case)
    name4 = ProductName("  samsung   galaxy   s24  ultra  ")
    print(name4.value)  # Samsung Galaxy S24 Ultra
    
    # These will raise ValueError
    try:
        name5 = ProductName("AB")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Product name must be 3-100 characters
    
    try:
        name6 = ProductName("Product@#$")
    except ValueError as e:
        print(f"Error: {e}")  # Error: Product name contains invalid characters
    
    try:
        name7 = ProductName("A" * 101)
    except ValueError as e:
        print(f"Error: {e}")  # Error: Product name must be 3-100 characters
