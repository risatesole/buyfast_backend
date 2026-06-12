from rest_framework.generics import ListAPIView
from ...models import Product
from .product_tags_serializer import ProductSerializer
from .product_tags_pagination import ProductCursorPagination

class ProductByTagView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductCursorPagination

    def get_queryset(self):
        tag = self.kwargs.get("tag")

        return (
            Product.objects
            .filter(tags__name=tag)
            .prefetch_related("images", "tags")
            .distinct()
            .order_by("-id")
        )
    