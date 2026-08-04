from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import random
import string

User = get_user_model()

class ForgotPasswordAPITestCase(TestCase):
    """Test cases for the forgot-password (request reset link) API"""

    def setUp(self):
        self.client = APIClient()
        self.forgot_password_url = reverse('api:auth-forgot-password')

    def generate_random_email(self):
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@example.com"

    def create_test_user(self, email=None, is_active=True):
        email = email or self.generate_random_email()
        user = User.objects.create_user(
            email=email,
            password='Str0ng!Pass123',
            first_name='Jane',
            last_name='Doe',
            is_active=is_active,
        )
        return user

    def test_forgot_password_existing_user_sends_email(self):
        user = self.create_test_user()

        response = self.client.post(
            self.forgot_password_url,
            data={"email": user.email},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].to)
        self.assertIn('reset-password?uid=', mail.outbox[0].body)
        self.assertIn('token=', mail.outbox[0].body)

    def test_forgot_password_nonexistent_email_does_not_leak(self):
        response = self.client.post(
            self.forgot_password_url,
            data={"email": self.generate_random_email()},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_disabled_account_does_not_send_email(self):
        user = self.create_test_user(is_active=False)

        response = self.client.post(
            self.forgot_password_url,
            data={"email": user.email},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_missing_email(self):
        response = self.client.post(
            self.forgot_password_url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

    def test_forgot_password_case_insensitive_email(self):
        user = self.create_test_user()

        response = self.client.post(
            self.forgot_password_url,
            data={"email": user.email.upper()},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
