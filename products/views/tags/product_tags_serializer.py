from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from ...models import Product, ProductImage, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "image",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "image_type",
        ]


class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
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
            "images",
        ]
