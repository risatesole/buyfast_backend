from django.db import IntegrityError

from ..models import Category


class CategoryAlreadyExistsError(Exception):
    """Raised when a category already exists."""

    pass


class CategoryService:
    def getCategories(self, status=None) -> list[dict]:
        categories = Category.objects.all()
        if status is not None:
            categories = categories.filter(status=status)
        return [self._serialize(c) for c in categories]

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

    def _serialize(self, category) -> dict:
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image or None,
            "status": category.status,
        }
