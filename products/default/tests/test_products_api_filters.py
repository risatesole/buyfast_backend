from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.default.models import Category, Product, ProductVariant


class ProductListFilterTests(APITestCase):
    def setUp(self):
        self.url = reverse("api:product-list")

        self.stationery = Category.objects.create(name="Papelería", slug="stationery")
        self.electronics = Category.objects.create(name="Electrónica", slug="electronics")
        self.books = Category.objects.create(name="Libros", slug="books")

        self.cheap_product = self._make_product(
            name="Lápiz",
            slug="pencil",
            category=self.stationery,
            price=Decimal("50.00"),
        )
        self.mid_product = self._make_product(
            name="Auriculares",
            slug="headphones",
            category=self.electronics,
            price=Decimal("150.00"),
        )
        self.expensive_product = self._make_product(
            name="Novela",
            slug="novel",
            category=self.books,
            price=Decimal("300.00"),
        )

    def _make_product(self, *, name, slug, category, price):
        product = Product.objects.create(name=name, slug=slug, category=category)
        ProductVariant.objects.create(
            product=product,
            name=name,
            description=f"Descripción de prueba para {name}",
            variantnumber=1,
            slug=f"{slug}-default",
            sku=f"SKU-{slug}",
            selling_price=price,
            tax_rate=Decimal("0.18"),
        )
        return product

    def _slugs(self, response):
        return {item["slug"] for item in response.data["data"]}

    def test_price_range_filters_products(self):
        response = self.client.get(self.url, {"price_min": "100", "price_max": "200"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._slugs(response), {"headphones"})

    def test_price_min_only(self):
        response = self.client.get(self.url, {"price_min": "150"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._slugs(response), {"headphones", "novel"})

    def test_category_filter_accepts_multiple_slugs(self):
        response = self.client.get(self.url, {"category": "stationery,books"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._slugs(response), {"pencil", "novel"})

    def test_category_and_price_filters_combine(self):
        response = self.client.get(
            self.url, {"category": "electronics,books", "price_min": "200"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._slugs(response), {"novel"})

    def test_price_bounds_reflect_full_catalog_regardless_of_filters(self):
        response = self.client.get(self.url, {"category": "stationery"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        price_bounds = response.data["meta"]["price_bounds"]
        self.assertEqual(price_bounds["min"], 50.0)
        self.assertEqual(price_bounds["max"], 300.0)

    def test_invalid_price_params_are_ignored(self):
        response = self.client.get(self.url, {"price_min": "not-a-number"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self._slugs(response), {"pencil", "headphones", "novel"}
        )
