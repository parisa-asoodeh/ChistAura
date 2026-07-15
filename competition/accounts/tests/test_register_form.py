from django.test import TestCase

from accounts.forms import RegisterForm
from accounts.models import CustomUser


class RegisterFormTest(TestCase):

    def test_register_form_accepts_unique_email(self):

        form = RegisterForm(
            data={
                "username": "user1",
                "email": "user1@test.com",
                "phone": "09120000000",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())


    def test_register_form_rejects_duplicate_email(self):

        CustomUser.objects.create_user(
            username="existing",
            email="user@test.com",
            password="StrongPass123!",
        )

        form = RegisterForm(
            data={
                "username": "user2",
                "email": "user@test.com",
                "phone": "09121111111",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "email",
            form.errors,
        )