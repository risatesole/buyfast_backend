from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
import random
import string

User = get_user_model()

class SignoutAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signout_url = reverse('api:auth-signout')
        self.signin_url = reverse('api:auth-signin')

        # Generate random user data
        self.random_email = self.generate_random_email()
        self.random_password = self.generate_random_password()
        self.random_firstname = self.generate_random_name()
        self.random_lastname = self.generate_random_name()

        self.test_user = User.objects.create_user(
            email=self.random_email,
            password=self.random_password,
            first_name=self.random_firstname,
            last_name=self.random_lastname
        )

    def generate_random_email(self):
        """Generate a random email address"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@example.com"

    def generate_random_password(self, length=12):
        """Generate a random strong password"""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(string.punctuation)
        ]
        password += [random.choice(characters) for _ in range(length - 4)]
        random.shuffle(password)
        return ''.join(password)

    def generate_random_name(self, length=None):
        """Generate a random name"""
        if length is None:
            length = random.randint(5, 12)
        return ''.join(random.choices(string.ascii_letters, k=length)).capitalize()

    def test_signout_works(self):
        """Test that signout endpoint works as intended"""
        # Sign in with random user
        self.client.post(
            self.signin_url,
            data={
                'email': self.random_email,
                'password': self.random_password
            },
            format='json'
        )

        # Sign out
        response = self.client.post(self.signout_url, format='json')

        # Verify successful signout
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'signout successful')

    def test_unauthenticated_signout_fails(self):
        """Test that unauthenticated users can't sign out"""
        response = self.client.post(self.signout_url, format='json')
        self.assertEqual(response.status_code, 403)
