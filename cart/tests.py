from django.contrib.auth import get_user_model
from django.test import TestCase

from products.models import Category, Product

from .cart import Cart

USER_CUSTOMER = {
    "username": "customer",
    "email": "customer@gmail.com",
    "password": "customer123",
}
USER_ADMIN = {
    "username": "admin",
    "email": "admin@gmail.com",
    "password": "admin123",
}
CATEGORY_1 = {"name": "clothes", "slug": "clothes"}
CATEGORY_2 = {"name": "food", "slug": "food"}
PRODUCT_1 = {
    "name": "Nike shoes",
    "slug": "nike-shoes",
    "description": "This are the famous nike shoes",
    "price": 14.5,
    "stock": 5,
}
PRODUCT_2 = {
    "name": "Green tea",
    "slug": "green-tea",
    "description": "Great beverage that helps you stay healthy",
    "price": 5.5,
    "stock": 1,
}
PRODUCT_3 = {
    "name": "Leather Nike jacket",
    "slug": "leather-nike-jacket",
    "description": "This is a custom made stylish piece of clothing",
    "price": 50,
    "stock": 2,
}


class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create product instances
        get_user_model().objects.create_user(**USER_CUSTOMER)
        superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
        cls.category = Category.objects.create(**CATEGORY_1)
        cls.product = Product.objects.create(
            **PRODUCT_1, category=cls.category, created_by=superuser
        )
        cls.product2 = Product.objects.create(
            **PRODUCT_2, category=cls.category, created_by=superuser
        )

    def test_cart_init_empty(self):
        cart = Cart(self.client)
        self.assertIsInstance(cart, Cart)
        self.assertEqual(len(cart), 0)

    def test_cart_add(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=3)
        self.assertEqual(len(cart), 3)
        self.assertEqual(list(cart)[0]["id"], str(self.product.pk))
        self.assertEqual(list(cart)[0]["quantity"], 3)

    def test_cart_remove(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=3)
        cart.remove(str(self.product.pk))
        self.assertEqual(len(cart), 0)

    def test_cart_len(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=2)
        self.assertEqual(len(cart), 2)

    def test_cart_iter(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=2)
        cart.add(self.product2.pk, quantity=3)
        self.assertEqual(len(list(cart)), 2)

    def test_cart_get_total_price(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=2)
        cart.add(self.product2.pk, quantity=3)
        _price = (self.product.price * 2) + (self.product2.price * 3)
        self.assertEqual(cart.total_price, _price)

    def test_cart_get_product(self):
        cart = Cart(self.client)
        cart.add(self.product.pk, quantity=2)
        cart.add(self.product2.pk, quantity=3)
        self.assertEqual(
            cart.get_product(str(self.product2.pk))["id"],
            str(self.product2.pk),
        )
