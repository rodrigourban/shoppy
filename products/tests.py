from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Favorite, Product, Review

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
REVIEW_1 = {"rating": 4, "content": "This are great shoes"}


class ProductTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create product instances
        user = get_user_model().objects.create_user(**USER_CUSTOMER)
        superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
        cls.category = Category.objects.create(**CATEGORY_1)
        cls.product = Product.objects.create(
            **PRODUCT_1, category=cls.category, created_by=superuser
        )
        cls.review = Review.objects.create(
            **REVIEW_1,
            product=cls.product,
            created_by=user,
        )
        cls.favorite = Favorite.objects.create(
            product=cls.product,
            created_by=user,
        )

    def test_product_display(self):
        self.assertEqual(self.product.name, "Nike shoes")
        self.assertEqual(self.product.description, "This are the famous nike shoes")
        self.assertEqual(self.product.price, 14.5)
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(self.product.category.name, "clothes")
        self.assertEqual(self.product.created_by.username, "admin")

    def test_product_list_view(self):
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nike shoes")
        self.assertTemplateUsed(response, "products/list.html")

    def test_product_detail_view(self):
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nike shoes")
        self.assertContains(response, "Stock: 5")
        # self.assertContains(response, '5 stars')
        self.assertContains(response, "1 review")
        # self.assertContains(response, 'This are great shoes')
        self.assertContains(response, "Add to Cart")
        self.assertTemplateUsed(response, "products/detail.html")

    def test_product_detail_view_admin(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nike shoes")
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, "Add to Favorite")
        self.assertTemplateUsed(response, "products/detail.html")
        self.client.logout()

    def test_product_detail_view_404(self):
        response = self.client.get("/products/not-found/")
        self.assertEqual(response.status_code, 404)

    def test_product_create_view_redirect_login(self):
        response = self.client.get(reverse("products:create"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next=/products/create/"
        )
        response = self.client.get(f"{reverse('account_login')}?next=/products/")
        self.assertContains(response, "Log in")

    def test_product_create_view_403(self):
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.get(reverse("products:create"))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_product_create_view(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        response = self.client.get(reverse("products:create"))
        # assert form
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create new product")
        self.assertTemplateUsed(response, "products/create.html")
        self.client.logout()

    def test_product_create_403(self):
        response = self.client.post(
            reverse("products:create"),
            {
                "name": "Test product",
                "description": "test description",
                "category": self.category.pk,
                "price": 20,
                "stock": 3,
            },
        )
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.post(
            reverse("products:create"),
            {
                "name": "Test product",
                "description": "test description",
                "category": self.category.pk,
                "price": 20,
                "stock": 3,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_product_create_duplicate_error(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        self.client.post(
            reverse("products:create"),
            {
                "name": "Test product",
                "description": "test description",
                "category": self.category.pk,
                "price": 20,
                "stock": 3,
            },
        )
        product = Product.objects.filter(name="Test product")
        self.assertEqual(len(product), 1)

    def test_product_create(self):
        response = self.client.post(
            reverse("products:create"),
            {
                "name": "Test product",
                "description": "test description",
                "category": self.category.pk,
                "price": 20,
                "stock": 3,
            },
        )
        self.assertEqual(response.status_code, 302)  # redirects to product list
        product = Product.objects.filter(name="Test product")
        self.assertIsNotNone(product)

    def test_product_update_view(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        response = self.client.get(reverse("products:update", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertTemplateUsed(response, "products/update.html")

    def test_product_update_view_404(self):
        response = self.client.get("products/update/12341")
        self.assertEqual(response.status_code, 404)

    def test_product_update_403(self):
        self.client.logout()
        response = self.client.get(reverse("products:update", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"""
            {reverse('account_login')}?next=/products/update/{self.product.pk}/
            """,
        )
        response = self.client.get(
            f"{reverse('account_login')}?next=/update/{self.product.pk}/"
        )
        self.assertContains(response, "Log in")
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.get(reverse("products:update", args=[self.product.pk]))
        self.assertEqual(response.status_code, 403)

    def test_product_update(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        self.client.post(
            reverse("products:update", args=[self.product.pk]),
            {
                "name": "New product name",
                "description": "new-product-name",
                "category": self.category.pk,
                "price": 25,
                "slug": "nike-shoes",
                "stock": 3,
            },
        )
        updated_product = Product.objects.filter(id=self.product.pk)
        self.assertEqual(updated_product[0].stock, 3)
        self.assertEqual(updated_product[0].name, "New product name")

    def test_product_update_stock_0_automatically_deactivate(self):
        self.client.login(email="admin@gmail.com", password="admin123")
        self.client.post(
            reverse("products:update", args=[self.product.pk]),
            {
                "name": "Nike shoes",
                "description": "test description",
                "slug": "nike-shoes",
                "category": self.category.pk,
                "price": 25,
                "stock": 0,
            },
        )
        product = Product.objects.filter(id=self.product.pk)
        self.assertEqual(product[0].stock, 0)
        self.assertEqual(product[0].available, False)


class FavoriteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create product instances
        user = get_user_model().objects.create_user(**USER_CUSTOMER)
        superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
        cls.category = Category.objects.create(**CATEGORY_1)
        cls.product = Product.objects.create(
            **PRODUCT_1, category=cls.category, created_by=superuser
        )
        cls.favorite = Favorite.objects.create(product=cls.product, created_by=user)

    def test_favorite_list_view_403_redirect(self):
        response = self.client.get(reverse("products:favorite_list"))
        self.assertEqual(response.status_code, 302)

    def test_favorite_list_view(self):
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.get(reverse("products:favorite_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nike shoes")
        self.assertTemplateUsed(response, "products/favorite_list.html")

    def test_favorite_toggle_403(self):
        self.client.logout()
        response = self.client.get(
            reverse("products:toggle_favorite", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_favorite_toggle(self):
        self.client.logout()
        self.client.login(email="customer@gmail.com", password="customer123")
        response = self.client.get(
            reverse("products:toggle_favorite", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add to favorite")
        response = self.client.get(
            reverse("products:toggle_favorite", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove favorite")


class ProductsSearchFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = get_user_model().objects.create_superuser(**USER_ADMIN)
        cls.url = reverse("products:search_filter")
        cls.category = Category.objects.create(**CATEGORY_1)
        cls.category2 = Category.objects.create(**CATEGORY_2)
        cls.product = Product.objects.create(
            **PRODUCT_1, category=cls.category, created_by=superuser
        )
        cls.product2 = Product.objects.create(
            **PRODUCT_2, category=cls.category2, created_by=superuser
        )
        cls.product3 = Product.objects.create(
            **PRODUCT_3, category=cls.category, created_by=superuser
        )

    def test_product_search_success(self):
        response = self.client.get(f"{self.url}?query=Tea")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product2.name)
        self.assertNotContains(response, self.product.name)
        self.assertNotContains(response, self.product3.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")

        response = self.client.get(f"{self.url}?query=nik")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product3.name)
        self.assertNotContains(response, self.product2.name)

        response = self.client.get(f"{self.url}?query=healthy")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product2.name)
        self.assertNotContains(response, self.product.name)
        self.assertNotContains(response, self.product3.name)

    def test_product_search_not_found(self):
        response = self.client.get(f"{self.url}?query=guitar")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Ups! There are no products matching your search,\
            please try something different!",
        )
        self.assertTemplateUsed(response, "products/partials/_list.html")

    def test_product_filter_price_range_from(self):
        response = self.client.get(f"{self.url}?price_from=6")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.product2.name)
        self.assertContains(response, self.product3.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")

        response = self.client.get(f"{self.url}?price_from=100")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.name)
        self.assertNotContains(response, self.product2.name)
        self.assertNotContains(response, self.product3.name)

    def test_product_filter_price_range_to(self):
        response = self.client.get(f"{self.url}?price_to=15")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product2.name)
        self.assertNotContains(response, self.product3.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")

        response = self.client.get(f"{self.url}?price_to=5")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.name)
        self.assertNotContains(response, self.product2.name)
        self.assertNotContains(response, self.product3.name)

    def test_product_filters_and_search_combined(self):
        response = self.client.get(
            f"{self.url}?category={self.category.pk}&query=nike&price_from=5&\
              price_to=16"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.product2.name)
        self.assertNotContains(response, self.product3.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")

    def test_product_filter_category(self):
        response = self.client.get(f"{self.url}?category={self.category.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product3.name)
        self.assertNotContains(response, self.product2.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")

    def test_product_filter_category_empty(self):
        response = self.client.get(f"{self.url}?category=")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product2.name)
        self.assertContains(response, self.product3.name)
        self.assertTemplateUsed(response, "products/partials/_list.html")


class ReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        return super().setUpTestData()

    def test_review_list_view(self):
        # only let you review once you bought the product
        pass

    def test_review_list_view_forbidden(self):
        # only let you review once you bought the product
        pass

    def test_review_list_view_404(self):
        pass

    def test_review_score_in_product_list_view(self):
        pass

    def test_review_create_view(self):
        # only let you review once you bought the product
        pass

    def test_review_create_view_duplicated(self):
        # Users can only review once per item
        pass
