# products/default/entities/product_normal_entity.py

from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# Use relative imports
from ..value_objects.product_name import ProductName
from ..value_objects.product_description import ProductDescription
from ..value_objects.product_sku import SKU
from ..value_objects.product_slug import Slug
from ..value_objects.product_category import ProductCategory
from ..value_objects.product_type import ProductType
from ..value_objects.product_selling_price import SellingPrice
from ..value_objects.product_taxrate import TaxRate
from ..value_objects.product_tags import Tags


@dataclass
class ProductNormalEntity:
    """
    A normal product entity with all standard fields.
    This represents a typical product in an e-commerce system.
    """

    # Core identity fields
    sku: SKU
    name: ProductName
    slug: Slug

    # Descriptive fields
    description: ProductDescription
    category: ProductCategory

    # Product type is locked to "normal" - hidden from constructor
    product_type: ProductType = field(default_factory=lambda: ProductType("normal"), init=False)

    # Pricing fields
    selling_price: SellingPrice
    tax_rate: TaxRate

    # Additional fields
    tags: Tags
    is_active: bool = True
    is_featured: bool = False
    stock_quantity: int = 0

    # Optional metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate the entity after initialization."""
        # Ensure product_type is always 'normal'
        if self.product_type.value != 'normal':
            raise ValueError("ProductNormalEntity must have product_type='normal'")

        if self.stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")

        # Set timestamps if not provided
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.now())

    def get_display_name(self) -> str:
        """Get the formatted product name for display."""
        return str(self.name)

    def get_price_with_tax(self) -> Decimal:
        """Calculate the price including tax."""
        return self.selling_price.value * (Decimal('1') + self.tax_rate.value)

    def is_in_stock(self) -> bool:
        """Check if the product is in stock."""
        return self.stock_quantity > 0 and self.is_active

    def update_stock(self, quantity: int) -> None:
        """Update stock quantity."""
        new_quantity = self.stock_quantity + quantity
        if new_quantity < 0:
            raise ValueError(f"Cannot reduce stock below 0. Current: {self.stock_quantity}, Adjustment: {quantity}")
        object.__setattr__(self, 'stock_quantity', new_quantity)
        self._update_timestamp()

    def activate(self) -> None:
        """Activate the product."""
        object.__setattr__(self, 'is_active', True)
        self._update_timestamp()

    def deactivate(self) -> None:
        """Deactivate the product."""
        object.__setattr__(self, 'is_active', False)
        self._update_timestamp()

    def feature(self) -> None:
        """Feature the product."""
        object.__setattr__(self, 'is_featured', True)
        self._update_timestamp()

    def unfeature(self) -> None:
        """Unfeature the product."""
        object.__setattr__(self, 'is_featured', False)
        self._update_timestamp()

    def add_tags(self, new_tags: List[str]) -> None:
        """Add new tags to the existing tags."""
        current_tags = self.tags.value
        combined_tags = current_tags + [tag.strip().lower() for tag in new_tags if tag.strip()]
        # Remove duplicates while preserving order
        unique_tags = []
        seen = set()
        for tag in combined_tags:
            if tag not in seen:
                unique_tags.append(tag)
                seen.add(tag)
        object.__setattr__(self, 'tags', Tags(unique_tags))
        self._update_timestamp()

    def remove_tag(self, tag_to_remove: str) -> None:
        """Remove a specific tag."""
        tag_to_remove = tag_to_remove.strip().lower()
        current_tags = self.tags.value
        if tag_to_remove not in current_tags:
            raise ValueError(f"Tag '{tag_to_remove}' not found")
        new_tags = [tag for tag in current_tags if tag != tag_to_remove]
        object.__setattr__(self, 'tags', Tags(new_tags))
        self._update_timestamp()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        object.__setattr__(self, 'updated_at', datetime.now())

    def to_dict(self) -> dict:
        """Convert entity to dictionary for serialization."""
        return {
            'sku': str(self.sku),
            'name': self.name.value,
            'slug': self.slug.value,
            'description': self.description.value,
            'category': self.category.value,
            'product_type': self.product_type.value,  # Will always be "normal"
            'selling_price': str(self.selling_price.value),
            'tax_rate': str(self.tax_rate.value),
            'tags': self.tags.value,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'stock_quantity': self.stock_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'price_with_tax': str(self.get_price_with_tax())
        }

    def __str__(self) -> str:
        """String representation of the product."""
        return f"Product(name='{self.name.value}', sku='{self.sku}', type='{self.product_type.value}', price={self.selling_price})"


# Example usage and testing
if __name__ == "__main__":
    from decimal import Decimal

    # Create a sample product - note we don't pass product_type
    product = ProductNormalEntity(
        sku=SKU("PROD-001"),
        name=ProductName("Wireless Bluetooth Headphones"),
        slug=Slug("wireless-bluetooth-headphones"),
        description=ProductDescription(
            "Premium wireless headphones with noise cancellation, "
            "30-hour battery life, and comfortable over-ear design."
        ),
        category=ProductCategory("electronics"),
        selling_price=SellingPrice(Decimal("199.99")),
        tax_rate=TaxRate(Decimal("0.08")),
        tags=Tags(["audio", "wireless", "premium"]),
        stock_quantity=50,
        is_active=True,
        is_featured=True
    )

    print("=== Product Created ===")
    print(product)
    print(f"Product Type: {product.product_type.value}")  # Will be "normal"
    print(f"Display Name: {product.get_display_name()}")
    print(f"Price with tax: ${product.get_price_with_tax():.2f}")
    print(f"In stock: {product.is_in_stock()}")
    print(f"Tags: {', '.join(product.tags.value)}")

    # Test update operations
    print("\n=== Testing Updates ===")
    print(f"Initial stock: {product.stock_quantity}")
    product.update_stock(-10)
    print(f"After selling 10: {product.stock_quantity}")

    product.add_tags(["new", "sale"])
    print(f"After adding tags: {', '.join(product.tags.value)}")

    product.remove_tag("premium")
    print(f"After removing 'premium': {', '.join(product.tags.value)}")

    # Test activation/deactivation
    print(f"\nActive: {product.is_active}")
    product.deactivate()
    print(f"After deactivation: {product.is_active}")
    product.activate()
    print(f"After reactivation: {product.is_active}")

    # Test feature/unfeature
    print(f"\nFeatured: {product.is_featured}")
    product.unfeature()
    print(f"After unfeature: {product.is_featured}")
    product.feature()
    print(f"After feature: {product.is_featured}")

    # Test dictionary conversion
    print("\n=== Product Dictionary ===")
    product_dict = product.to_dict()
    for key, value in product_dict.items():
        print(f"{key}: {value}")

    # Test validation - negative stock
    print("\n=== Testing Validation ===")
    try:
        invalid_product = ProductNormalEntity(
            sku=SKU("PROD-002"),
            name=ProductName("Test Product"),
            slug=Slug("test-product"),
            description=ProductDescription("Valid description here"),
            category=ProductCategory("electronics"),
            selling_price=SellingPrice(Decimal("99.99")),
            tax_rate=TaxRate(Decimal("0.08")),
            tags=Tags(["test"]),
            stock_quantity=-5  # Invalid
        )
    except ValueError as e:
        print(f"Validation error caught: {e}")

    # Test adding tags with duplicate
    print("\n=== Testing Duplicate Tags ===")
    product.add_tags(["audio", "new"])
    print(f"After adding duplicate 'audio': {', '.join(product.tags.value)}")

    # Test removing non-existent tag
    try:
        product.remove_tag("nonexistent")
    except ValueError as e:
        print(f"Error caught: {e}")
