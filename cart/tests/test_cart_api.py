# cart/tests/test_cart_api.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from products.default.models import (
    Product,
    ProductVariant,
    ProductImage,
)

User = get_user_model()


class CartAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="Password123!",
        )

        self.client.force_authenticate(self.user)

        self.product = Product.objects.create(
            name="Notebook",
            slug="notebook",
            category=Product.Category.STATIONERY,
            product_type=Product.ProductType.PHYSICAL,
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="Default",
            description="",
            variantnumber=1,
            slug="notebook-default",
            sku="SKU-001",
            selling_price=Decimal("100.00"),
            tax_rate=Decimal("18.00"),
        )

        ProductImage.objects.create(
            product_variant=self.variant,
            image="https://example.com/image.jpg",
            image_type=ProductImage.ImageType.THUMBNAIL,
        )

        self.url = reverse("api:cart-api")

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def test_add_product_to_cart(self):
        response = self.client.post(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart)

        self.assertEqual(item.variant, self.variant)
        self.assertEqual(item.quantity, 2)

        self.assertEqual(response.data["status"], "ok")

    def test_add_same_product_twice_increases_quantity(self):
        self.client.post(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        response = self.client.post(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = CartItem.objects.get()

        self.assertEqual(item.quantity, 5)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_post_invalid_variant_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "productvariantid": 999999,
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def test_get_empty_cart(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["data"]["items"], [])

    def test_get_cart_returns_items(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=4,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["items"]), 1)

    # --------------------------------------------------------
    # PATCH
    # --------------------------------------------------------

    def test_patch_updates_quantity(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1,
        )

        response = self.client.patch(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 10,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = CartItem.objects.get()
        self.assertEqual(item.quantity, 10)

    def test_patch_nonexistent_item_returns_404(self):
        response = self.client.patch(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_missing_quantity_returns_400(self):
        response = self.client.patch(
            self.url,
            {
                "productvariantid": self.variant.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def test_delete_decreases_quantity(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=5,
        )

        response = self.client.delete(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = CartItem.objects.get()
        self.assertEqual(item.quantity, 3)

    def test_delete_removes_item_when_quantity_reaches_zero(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=2,
        )

        response = self.client.delete(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            CartItem.objects.filter(cart=cart).exists()
        )

    def test_delete_more_than_quantity_removes_item(self):
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=2,
        )

        response = self.client.delete(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 10,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(CartItem.objects.exists())

    def test_delete_nonexistent_item_returns_404(self):
        response = self.client.delete(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_invalid_payload_returns_400(self):
        response = self.client.delete(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    def test_get_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_post_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.post(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_patch_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.patch(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_delete_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.delete(
            self.url,
            {
                "productvariantid": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
