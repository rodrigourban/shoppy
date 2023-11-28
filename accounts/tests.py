from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CustomUserTests(TestCase):
    def test_create_user(self):
        new_user = get_user_model().objects.create_user(
            username="newuser",
            email="newuser@gmail.com",
            password="testpassword123",
        )
        self.assertEqual(new_user.username, "newuser")
        self.assertEqual(new_user.email, "newuser@gmail.com")
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

    def test_create_super_user(self):
        new_user = get_user_model().objects.create_superuser(
            username="superman",
            email="superman@gmail.com",
            password="testpassword123",
        )
        self.assertEqual(new_user.username, "superman")
        self.assertEqual(new_user.email, "superman@gmail.com")
        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.is_staff)
        self.assertTrue(new_user.is_superuser)


class SignupPageTest(TestCase):
    username = "newuser"
    email = "newuser@shoppy.com"

    def setUp(self):
        url = reverse("account_signup")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/signup.html")
        self.assertContains(self.response, "Welcome, join Shoppy!")
        self.assertNotContains(self.response, "This shouldnt be part of the page")

    def test_signup_form(self):
        get_user_model().objects.create_user(self.username, self.email)
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, self.username)
        self.assertEqual(users[0].email, self.email)
