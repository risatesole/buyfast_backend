from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
import random
import string

User = get_user_model()

class ResetPasswordAPITestCase(TestCase):
    """Test cases for the reset-password (confirm new password) API"""

    def setUp(self):
        self.client = APIClient()
        self.reset_password_url = reverse('api:auth-reset-password')

    def generate_random_email(self):
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@example.com"

    def create_test_user(self, password='OldStr0ng!Pass'):
        user = User.objects.create_user(
            email=self.generate_random_email(),
            password=password,
            first_name='Jane',
            last_name='Doe',
        )
        return user

    def make_uid_and_token(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    def test_reset_password_success(self):
        user = self.create_test_user()
        uid, token = self.make_uid_and_token(user)

        response = self.client.post(
            self.reset_password_url,
            data={"uid": uid, "token": token, "new_password": "NewStr0ng!Pass456"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStr0ng!Pass456"))

    def test_reset_password_invalid_token(self):
        user = self.create_test_user()
        uid, _ = self.make_uid_and_token(user)

        response = self.client.post(
            self.reset_password_url,
            data={"uid": uid, "token": "not-a-real-token", "new_password": "NewStr0ng!Pass456"},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

    def test_reset_password_invalid_uid(self):
        response = self.client.post(
            self.reset_password_url,
            data={"uid": "not-a-real-uid", "token": "irrelevant", "new_password": "NewStr0ng!Pass456"},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

    def test_reset_password_token_cannot_be_reused(self):
        user = self.create_test_user()
        uid, token = self.make_uid_and_token(user)

        first_response = self.client.post(
            self.reset_password_url,
            data={"uid": uid, "token": token, "new_password": "NewStr0ng!Pass456"},
            format='json'
        )
        self.assertEqual(first_response.status_code, 200)

        second_response = self.client.post(
            self.reset_password_url,
            data={"uid": uid, "token": token, "new_password": "AnotherStr0ng!Pass789"},
            format='json'
        )
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(second_response.data['status'], 'error')

    def test_reset_password_missing_fields(self):
        response = self.client.post(
            self.reset_password_url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

    def test_reset_password_weak_password_rejected(self):
        user = self.create_test_user()
        uid, token = self.make_uid_and_token(user)

        response = self.client.post(
            self.reset_password_url,
            data={"uid": uid, "token": token, "new_password": "123"},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

        user.refresh_from_db()
        self.assertTrue(user.check_password('OldStr0ng!Pass'))
