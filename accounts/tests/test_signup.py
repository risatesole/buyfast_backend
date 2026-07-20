from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APIClient

User = get_user_model()

class SignupAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('api:auth-signup')

    def test_successful_signup(self):
        """Test successful user signup"""
        signup_data = {
            "firstname": "John",
            "lastname": "Doe",
            "email": "john.doe@example.com",
            "password": "StrongPass123!",
            "phone": "809-555-1234",
            "matricula": "2023-1234",
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
        self.assertTrue(User.objects.filter(email='john.doe@example.com').exists())
        user = User.objects.get(email='john.doe@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.matricula, '2023-1234')
        self.assertEqual(user.phone_number, '809-555-1234')

        # Check email was sent (use .to instead of .recipient_list)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '¡Bienvenido al Economato UASD!')
        self.assertIn('john.doe@example.com', mail.outbox[0].to)

        # Check response contains user data
        self.assertEqual(response.data['data']['user']['firstname'], 'John')
        self.assertEqual(response.data['data']['user']['lastname'], 'Doe')
        self.assertEqual(response.data['data']['user']['email'], 'john.doe@example.com')

    def test_signup_invalid_data(self):
        """Test signup with invalid data"""
        invalid_data = {
            "firstname": "",  # Empty first name
            "lastname": "Doe",
            "email": "invalid-email",  # Invalid email format
            "password": "weak",  # Weak password
            "phone": "809-555-1234",
            "matricula": "2023-1234",
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=invalid_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('errors', response.data)

        # User should not be created
        self.assertEqual(User.objects.count(), 0)

    def test_signup_duplicate_email(self):
        """Test signup with existing email"""
        # Create a user first
        User.objects.create_user(
            email='existing@example.com',
            password='StrongPass123!',
            first_name='Existing',
            last_name='User'
        )

        signup_data = {
            "firstname": "John",
            "lastname": "Doe",
            "email": "existing@example.com",  # Duplicate email
            "password": "StrongPass123!",
            "phone": "809-555-1234",
            "matricula": "2023-1234",
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
        # Check for error message (may be in different key)
        self.assertIn('message', response.data)
        self.assertIn('Signup need fields to be filled', response.data['message'])

    def test_signup_missing_required_fields(self):
        """Test signup with missing required fields"""
        incomplete_data = {
            "firstname": "John",
            "lastname": "Doe",
            # Missing email, password, phone, matricula
            "terms": True
        }

        response = self.client.post(
            self.signup_url,
            data=incomplete_data,
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
            "firstname": "John",
            "lastname": "Doe",
            "email": "john.weak@example.com",
            "password": "123",  # Too weak
            "phone": "809-555-1234",
            "matricula": "2023-1234",
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

    def test_signup_response_structure(self):
        """Test that successful signup response has correct structure"""
        signup_data = {
            "firstname": "Jane",
            "lastname": "Smith",
            "email": "jane.smith@example.com",
            "password": "SecurePass456!",
            "phone": "809-555-5678",
            "matricula": "2023-5678",
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
