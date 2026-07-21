from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APIClient
import random
import string

User = get_user_model()

class SignupAPITestCase(TestCase):
    """Test cases for signup API with randomly generated test data"""

    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('api:auth-signup')
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

    def generate_random_name(self, length=None):
        """Generate a random name"""
        if length is None:
            length = random.randint(5, 12)
        return ''.join(random.choices(string.ascii_letters, k=length)).capitalize()

    def generate_random_phone(self):
        """Generate a random phone number"""
        return f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    def generate_random_matricula(self):
        """Generate a random matricula"""
        year = random.randint(2020, 2024)
        number = random.randint(1000, 9999)
        return f"{year}-{number}"

    def test_successful_signup_with_random_data(self):
        """Test successful signup with randomly generated data"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Check response status and data
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'signup successfully')

        # Check user was created with correct data
        self.assertTrue(User.objects.filter(email=signup_data['email']).exists())
        user = User.objects.get(email=signup_data['email'])
        self.assertEqual(user.first_name, signup_data['firstname'])
        self.assertEqual(user.last_name, signup_data['lastname'])
        self.assertEqual(user.matricula, signup_data['matricula'])
        self.assertEqual(user.phone_number, signup_data['phone'])

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '¡Bienvenido al Economato UASD!')
        self.assertIn(signup_data['email'], mail.outbox[0].to)

        # Check response contains user data
        self.assertEqual(response.data['data']['user']['firstname'], signup_data['firstname'])
        self.assertEqual(response.data['data']['user']['lastname'], signup_data['lastname'])
        self.assertEqual(response.data['data']['user']['email'], signup_data['email'])

    def test_signup_invalid_email_format(self):
        """Test signup with invalid email format"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": "invalid-email-format",
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_empty_firstname(self):
        """Test signup with empty first name"""
        signup_data = {
            "firstname": "",
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_duplicate_email_random_data(self):
        """Test signup with existing random email"""
        # Create a user first with random data
        existing_email = self.generate_random_email()
        User.objects.create_user(
            email=existing_email,
            password=self.generate_random_password(),
            first_name=self.generate_random_name(),
            last_name=self.generate_random_name()
        )

        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": existing_email,  # Duplicate email
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Check error response for duplicate email
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

        # Only one user should exist (the original one)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_get_method(self):
        """Test GET method returns error"""
        response = self.client.get(self.signup_url)

        # GET requests should return 400 error
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.data)
        self.assertIn('Signup need fields to be filled', response.data['message'])

    def test_signup_missing_email(self):
        """Test signup with missing email field"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Should return validation error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_missing_password(self):
        """Test signup with missing password field"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Should return validation error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": "123",  # Too weak
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Should return error due to weak password
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_response_structure_random_data(self):
        """Test response structure with randomly generated data"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        # Check response structure
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertIn('user', response.data['data'])
        self.assertIn('terms', response.data['data'])

        # Check user data structure
        user_data = response.data['data']['user']
        self.assertIn('id', user_data)
        self.assertIn('firstname', user_data)
        self.assertIn('lastname', user_data)
        self.assertIn('email', user_data)
        self.assertIn('role', user_data)
        self.assertIn('phonenumber', user_data)
        self.assertIn('matricula', user_data)

    def test_signup_multiple_attempts_random_data(self):
        """Test multiple signup attempts with random data"""
        for _ in range(3):
            signup_data = {
                "firstname": self.generate_random_name(),
                "lastname": self.generate_random_name(),
                "email": self.generate_random_email(),
                "password": self.generate_random_password(),
                "phone": self.generate_random_phone(),
                "matricula": self.generate_random_matricula(),
                "terms": True
            }

            response = self.client.post(
                self.signup_url,
                data=signup_data,
                format='json'
            )

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['status'], 'ok')

        # Verify all 3 users were created
        self.assertEqual(User.objects.count(), 3)

    def test_signup_with_special_characters_password(self):
        """Test signup with complex password containing special characters"""
        complex_password = self.generate_random_password(length=16)
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": complex_password,
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'ok')

        # Verify user was created
        user = User.objects.get(email=signup_data['email'])
        self.assertEqual(user.first_name, signup_data['firstname'])

    def test_signup_all_fields_valid_random_data(self):
        """Test signup with all fields valid and random"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'signup successfully')

        # Verify all data matches
        user = User.objects.get(email=signup_data['email'])
        self.assertEqual(user.first_name, signup_data['firstname'])
        self.assertEqual(user.last_name, signup_data['lastname'])
        self.assertEqual(user.email, signup_data['email'])
        self.assertEqual(user.phone_number, signup_data['phone'])
        self.assertEqual(user.matricula, signup_data['matricula'])

    def test_signup_stress_test_random_users(self):
        """Stress test with multiple random user signups"""
        num_users = 5

        for _ in range(num_users):
            signup_data = {
                "firstname": self.generate_random_name(),
                "lastname": self.generate_random_name(),
                "email": self.generate_random_email(),
                "password": self.generate_random_password(),
                "phone": self.generate_random_phone(),
                "matricula": self.generate_random_matricula(),
                "terms": True
            }

            response = self.client.post(
                self.signup_url,
                data=signup_data,
                format='json'
            )

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['status'], 'ok')

        # Verify all users were created
        self.assertEqual(User.objects.count(), num_users)

    def test_signup_empty_lastname(self):
        """Test signup with empty last name"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": "",
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_terms_false(self):
        """Test signup with terms not accepted"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula(),
            "terms": False  # Terms not accepted
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Should return error or validation error
        self.assertEqual(response.status_code, 400)

    def test_signup_missing_terms_field(self):
        """Test signup with missing terms field"""
        signup_data = {
            "firstname": self.generate_random_name(),
            "lastname": self.generate_random_name(),
            "email": self.generate_random_email(),
            "password": self.generate_random_password(),
            "phone": self.generate_random_phone(),
            "matricula": self.generate_random_matricula()
            # Missing terms field
        }

        response = self.client.post(
            self.signup_url,
            data=signup_data,
            format='json'
        )

        # Should return validation error
        self.assertEqual(response.status_code, 400)
