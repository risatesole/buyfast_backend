from ..models import Category

class CategoryService:

    def getCategories(self, status=None) -> list[dict]:
        categories = Category.objects.all()
        if status is not None:
            categories = categories.filter(status=status)
        return [self._serialize(c) for c in categories]

    def setCategory(self, name, slug, description="", image="", status=True) -> dict:
        category = Category.objects.create(
            name=name,
            slug=slug,
            description=description,
            image=image,
            status=status,
        )
        return self._serialize(category)

    def _serialize(self, category) -> dict:
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image or None,
            "status": category.status,
        }
