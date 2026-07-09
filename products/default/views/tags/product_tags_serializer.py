from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from ...models import Product

class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "brand",
            "metric_unit",
            "selling_price",
            "status",
            "category",
            "tags",
        ]
