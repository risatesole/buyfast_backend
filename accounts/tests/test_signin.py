from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import random
import string

User = get_user_model()

class SigninAPITestCase(TestCase):
    """Test cases for signin API with randomly generated test data"""

    def setUp(self):
        self.client = APIClient()
        self.signin_url = reverse('api:auth-signin')
        self.test_users = []

    def generate_random_email(self):
        """Generate a random email address"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@example.com"

    def generate_random_password(self, length=12):
        """Generate a random strong password"""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = [
            random.choice(string.ascii_uppercase),  # At least one uppercase
            random.choice(string.ascii_lowercase),  # At least one lowercase
            random.choice(string.digits),           # At least one digit
            random.choice(string.punctuation)       # At least one special char
        ]
        password += [random.choice(characters) for _ in range(length - 4)]
        random.shuffle(password)
        return ''.join(password)

    def generate_random_name(self, length=8):
        """Generate a random name"""
        return ''.join(random.choices(string.ascii_letters, k=length)).capitalize()

    def create_test_user(self, email=None, password=None, first_name=None, last_name=None, is_active=True):
        """Helper to create a test user with random or provided data"""
        email = email or self.generate_random_email()
        password = password or self.generate_random_password()
        first_name = first_name or self.generate_random_name()
        last_name = last_name or self.generate_random_name()

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active
        )
        user.role = random.choice(['customer', 'employee', 'admin'])
        user.save()
        self.test_users.append({'user': user, 'password': password})
        return user, password

    def test_successful_signin_with_random_data(self):
        """Test successful signin with randomly generated user data"""
        user, password = self.create_test_user()

        signin_data = {
            "email": user.email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'signin successful')
        self.assertEqual(response.data['data']['user']['id'], user.id)
        self.assertEqual(response.data['data']['user']['email'], user.email)
        self.assertEqual(response.data['data']['user']['role'], user.role)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signin_invalid_email_random_password(self):
        """Test signin with random non-existent email"""
        fake_email = self.generate_random_email()
        fake_password = self.generate_random_password()

        signin_data = {
            "email": fake_email,
            "password": fake_password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid email or password')

    def test_signin_invalid_password_random_user(self):
        """Test signin with correct email but wrong random password"""
        user, _ = self.create_test_user()
        wrong_password = self.generate_random_password()

        signin_data = {
            "email": user.email,
            "password": wrong_password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid email or password')

    def test_signin_empty_email_random_password(self):
        """Test signin with empty email and random password"""
        signin_data = {
            "email": "",
            "password": self.generate_random_password()
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_empty_password_random_user(self):
        """Test signin with random user email but empty password"""
        user, _ = self.create_test_user()

        signin_data = {
            "email": user.email,
            "password": ""
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_missing_email_random_password(self):
        """Test signin with missing email field"""
        signin_data = {
            "password": self.generate_random_password()
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_missing_password_random_user(self):
        """Test signin with missing password field"""
        user, _ = self.create_test_user()

        signin_data = {
            "email": user.email
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_disabled_account_random_user(self):
        """Test signin with randomly created disabled account"""
        user, password = self.create_test_user(is_active=False)

        signin_data = {
            "email": user.email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'User account is disabled')

    def test_signin_case_insensitive_email_random_user(self):
        """Test signin with uppercase version of random email"""
        user, password = self.create_test_user()
        uppercase_email = user.email.upper()

        signin_data = {
            "email": uppercase_email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['data']['user']['id'], user.id)

    def test_signin_mixed_case_email_random_user(self):
        """Test signin with mixed case version of random email"""
        user, password = self.create_test_user()
        mixed_case_email = ''.join(
            c.upper() if random.choice([True, False]) else c.lower()
            for c in user.email
        )

        signin_data = {
            "email": mixed_case_email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_signin_email_with_whitespace_random_user(self):
        """Test signin with random email containing surrounding whitespace"""
        user, password = self.create_test_user()
        email_with_whitespace = f"  {user.email}  "

        signin_data = {
            "email": email_with_whitespace,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_signin_response_structure_random_user(self):
        """Test response structure with randomly generated user"""
        user, password = self.create_test_user()

        signin_data = {
            "email": user.email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        # Check response structure
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertIn('user', response.data['data'])

        # Check user data structure
        user_data = response.data['data']['user']
        self.assertIn('id', user_data)
        self.assertIn('firstname', user_data)
        self.assertIn('lastname', user_data)
        self.assertIn('email', user_data)
        self.assertIn('role', user_data)

    def test_signin_multiple_attempts_random_user(self):
        """Test multiple signin attempts with random user"""
        user, password = self.create_test_user()

        signin_data = {
            "email": user.email,
            "password": password
        }

        # First attempt
        response1 = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )
        self.assertEqual(response1.status_code, 200)

        # Second attempt should also succeed
        response2 = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )
        self.assertEqual(response2.status_code, 200)

    def test_signin_with_special_characters_password_random_user(self):
        """Test signin with random user and complex password"""
        complex_password = self.generate_random_password(length=16)
        user, _ = self.create_test_user(password=complex_password)

        signin_data = {
            "email": user.email,
            "password": complex_password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['data']['user']['id'], user.id)

    def test_signin_no_json_data_random_user(self):
        """Test signin with no data sent"""
        response = self.client.post(
            self.signin_url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_different_random_users(self):
        """Test signin with multiple randomly generated users"""
        # Create multiple random users
        users_data = [self.create_test_user() for _ in range(3)]

        for user, password in users_data:
            signin_data = {
                "email": user.email,
                "password": password
            }

            response = self.client.post(
                self.signin_url,
                data=signin_data,
                format='json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['status'], 'ok')
            self.assertEqual(response.data['data']['user']['id'], user.id)
            self.assertEqual(response.data['data']['user']['role'], user.role)

    def test_signin_preserves_user_state_random_user(self):
        """Test that signin returns correct random user state"""
        user, password = self.create_test_user()
        random_role = random.choice(['admin', 'manager', 'staff'])
        user.role = random_role
        user.save()

        signin_data = {
            "email": user.email,
            "password": password
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['user']['role'], random_role)

    def test_signin_stress_test_random_users(self):
        """Stress test with multiple random users and signin attempts"""
        # Create 5 random users
        users = [self.create_test_user() for _ in range(5)]

        # Try signing in as each user twice
        for user, password in users:
            for _ in range(2):
                signin_data = {
                    "email": user.email,
                    "password": password
                }

                response = self.client.post(
                    self.signin_url,
                    data=signin_data,
                    format='json'
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['data']['user']['id'], user.id)
