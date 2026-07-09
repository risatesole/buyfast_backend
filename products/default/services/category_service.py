from django.db import IntegrityError
from django.shortcuts import get_object_or_404

# from ..models import Category


class CategoryAlreadyExistsError(Exception):
    """Raised when a category already exists."""

    pass


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""

    pass


class CategoryService:
    def getCategories(self, status=None) -> list[dict]:
        pass

    def getCategoryById(self, category_id: int) -> dict | None:
        """Get a single category by ID."""
        pass

    def setCategory(self, name, slug, description="", image="", status=True) -> dict:
       pass

    def updateCategory(self, category_id: int, **kwargs) -> dict:
        """Update an existing category."""
        pass

    def deleteCategory(self, category_id: int) -> bool:
        """Delete a category by ID."""
        pass

    def _serialize(self, category) -> dict:
        pass 
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image or None,
            "status": category.status,
        }
