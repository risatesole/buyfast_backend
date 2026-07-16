from enum import Enum
from typing import Optional

# Si usas Python 3.11+, puedes heredar de StrEnum en lugar de str, Enum.
# En el ecosistema Django, lo ideal es heredar de django.db.models.TextChoices.
class ProductCategory(str, Enum):
    """
    Categorías alineadas al dominio del economato de la UASD.
    Heredar de 'str' permite que la serialización (ej. JSON/DRF) funcione nativamente.
    """
    STATIONERY = 'stationery'
    BOOKS_MANUALS = 'books_manuals'
    MEDICAL_LAB = 'medical_lab'
    ARCHITECTURE_ARTS = 'architecture_arts'
    ELECTRONICS = 'electronics'
    UNIFORMS = 'uniforms'
    SNACKS_BEVERAGES = 'snacks_beverages'

    @classmethod
    def from_optional(cls, value: Optional[str]) -> Optional['ProductCategory']:
        if value is None:
            return None
        try:
            return cls(value)
        except ValueError:
            # cls._value2member_map_ o una comprensión simple para obtener valores válidos
            valid_categories = [e.value for e in cls]
            raise ValueError(f"Categoría inválida. Debe ser una de: {', '.join(valid_categories)}")

    def __str__(self) -> str:
        return self.value

if __name__ == "__main__":
    # Instanciación correcta y validada por el Enum
    cat1 = ProductCategory("electronics")
    print(cat1)  # electronics
    
    cat2 = ProductCategory.from_optional("stationery")
    print(cat2)  # stationery
    
    cat3 = ProductCategory.from_optional(None)
    print(cat3)  # None
    
    # Manejo de excepciones consistente
    try:
        cat4 = ProductCategory("beauty") # Falla porque no existe en el dominio UASD
    except ValueError as e:
        print(f"Error: {e}")