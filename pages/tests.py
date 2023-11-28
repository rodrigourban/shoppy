from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PagesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        get_user_model().objects.create_user(
            username="customer",
            email="customer@gmail.com",
            password="testpassword123",
        )
        get_user_model().objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="testpassword123",
        )

    def test_home_view_render(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FAQ")
        self.assertContains(response, "About")
        self.assertContains(response, "Browse")
        self.assertContains(response, "Login")
        self.assertTemplateUsed(response, "home.html")

    def test_home_view_logged_nav_links(self):
        self.client.login(username="customer", password="testpassword123")
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, "Logout")
        self.assertContains(response, "Cart")
        self.assertContains(response, "Inbox")
        self.assertContains(response, "My account")

    def test_home_view_admin_logged_nav_links(self):
        self.client.logout()
        self.client.login(username="admin", password="testpassword123")
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, "Logout")
        self.assertContains(response, "New product")
        self.assertContains(response, "Inbox")

    def test_about_view_render(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Shoppy, your one-stop")
        self.assertTemplateUsed(response, "about.html")

    def test_faq_view_render(self):
        response = self.client.get(reverse("pages:faq"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frequently Asked Questions")
        self.assertTemplateUsed(response, "faq.html")
