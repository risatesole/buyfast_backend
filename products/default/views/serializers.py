from rest_framework import serializers
from datetime import datetime


class ProductVariantSerializer(serializers.Serializer):
    """Serializer for ProductVariant - converts variant data to JSON"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    sku = serializers.CharField()
    slug = serializers.CharField()
    selling_price = serializers.FloatField()
    tax_rate = serializers.FloatField()
    image_hero = serializers.CharField(allow_null=True, required=False)
    image_thumbnail = serializers.CharField(allow_null=True, required=False)
    image_gallery = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')


class ProductDetailSerializer(serializers.Serializer):
    """Serializer for Product with all variants"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    product_type = serializers.CharField()
    tags = serializers.JSONField(allow_null=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')
    variants = ProductVariantSerializer(many=True, read_only=True)


class ProductListSerializer(serializers.Serializer):
    """Serializer for Product list (minimal info)"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    thumbnail = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')
