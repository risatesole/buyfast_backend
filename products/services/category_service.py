from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from ..models import Category


class CategoryAlreadyExistsError(Exception):
    """Raised when a category already exists."""

    pass


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""

    pass


class CategoryService:
    def getCategories(self, status=None) -> list[dict]:
        categories = Category.objects.all()
        if status is not None:
            categories = categories.filter(status=status)
        return [self._serialize(c) for c in categories]

    def getCategoryById(self, category_id: int) -> dict | None:
        """Get a single category by ID."""
        try:
            category = Category.objects.get(id=category_id)
            return self._serialize(category)
        except Category.DoesNotExist:
            return None

    def setCategory(self, name, slug, description="", image="", status=True) -> dict:
        try:
            category = Category.objects.create(
                name=name,
                slug=slug,
                description=description,
                image=image,
                status=status,
            )
            return self._serialize(category)

        except IntegrityError as e:
            if "slug" in str(e).lower():
                raise CategoryAlreadyExistsError(
                    f"Category with slug '{slug}' already exists."
                ) from e
            raise

    def updateCategory(self, category_id: int, **kwargs) -> dict:
        """Update an existing category."""
        try:
            category = Category.objects.get(id=category_id)
            
            # Update only the fields that are provided
            if 'name' in kwargs:
                category.name = kwargs['name']
            if 'slug' in kwargs:
                category.slug = kwargs['slug']
            if 'description' in kwargs:
                category.description = kwargs['description']
            if 'image' in kwargs:
                category.image = kwargs['image']
            if 'status' in kwargs:
                category.status = kwargs['status']
            
            try:
                category.save()
                return self._serialize(category)
            except IntegrityError as e:
                if "slug" in str(e).lower():
                    raise CategoryAlreadyExistsError(
                        f"Category with slug '{kwargs.get('slug')}' already exists."
                    ) from e
                raise
                
        except Category.DoesNotExist:
            raise CategoryNotFoundError(f"Category with id '{category_id}' not found.")

    def deleteCategory(self, category_id: int) -> bool:
        """Delete a category by ID."""
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return True
        except Category.DoesNotExist:
            return False

    def _serialize(self, category) -> dict:
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image or None,
            "status": category.status,
        }
