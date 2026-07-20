from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class SigninAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signin_url = reverse('api:auth-signin')

        # Create a test user for signin tests
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.test_user.role = 'customer'
        self.test_user.save()

    def test_successful_signin(self):
        """Test successful user signin with valid credentials"""
        signin_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check response status and data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'signin successful')

        # Check user data in response
        self.assertEqual(response.data['data']['user']['id'], self.test_user.id)
        self.assertEqual(response.data['data']['user']['firstname'], 'Test')
        self.assertEqual(response.data['data']['user']['lastname'], 'User')
        self.assertEqual(response.data['data']['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['data']['user']['role'], 'customer')

        # Check user is authenticated in session
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.id, self.test_user.id)

    def test_signin_invalid_email(self):
        """Test signin with non-existent email"""
        signin_data = {
            "email": "nonexistent@example.com",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid email or password')

    def test_signin_invalid_password(self):
        """Test signin with incorrect password"""
        signin_data = {
            "email": "testuser@example.com",
            "password": "WrongPassword123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid email or password')

    def test_signin_empty_email(self):
        """Test signin with empty email"""
        signin_data = {
            "email": "",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_empty_password(self):
        """Test signin with empty password"""
        signin_data = {
            "email": "testuser@example.com",
            "password": ""
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_missing_email(self):
        """Test signin with missing email field"""
        signin_data = {
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_missing_password(self):
        """Test signin with missing password field"""
        signin_data = {
            "email": "testuser@example.com"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_disabled_account(self):
        """Test signin with disabled account"""
        # Deactivate the user
        self.test_user.is_active = False
        self.test_user.save()

        signin_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Check error response for disabled account
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'User account is disabled')

    def test_signin_case_insensitive_email(self):
        """Test signin with uppercase email (should work with email normalization)"""
        signin_data = {
            "email": "TESTUSER@EXAMPLE.COM",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        # Email should be case-insensitive due to normalization in view
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['data']['user']['id'], self.test_user.id)

    def test_signin_mixed_case_email(self):
        """Test signin with mixed case email"""
        signin_data = {
            "email": "TestUser@Example.Com",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_signin_email_with_whitespace(self):
        """Test signin with email containing whitespace"""
        signin_data = {
            "email": "  testuser@example.com  ",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_signin_response_structure(self):
        """Test that successful signin response has correct structure"""
        signin_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
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

    def test_signin_multiple_attempts(self):
        """Test multiple signin attempts (should work independently)"""
        signin_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
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

    def test_signin_with_special_characters_in_password(self):
        """Test signin with special characters in password"""
        # Create user with special characters in password
        special_user = User.objects.create_user(
            email='special@example.com',
            password='P@ssw0rd!#$%',
            first_name='Special',
            last_name='User'
        )

        signin_data = {
            "email": "special@example.com",
            "password": "P@ssw0rd!#$%"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['data']['user']['id'], special_user.id)

    def test_signin_no_json_data(self):
        """Test signin with no data sent"""
        response = self.client.post(
            self.signin_url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')

    def test_signin_different_users(self):
        """Test signin with different users"""
        # Create another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User'
        )
        other_user.role = 'employee'
        other_user.save()

        # Signin as first user
        response1 = self.client.post(
            self.signin_url,
            data={"email": "testuser@example.com", "password": "TestPass123!"},
            format='json'
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['data']['user']['role'], 'customer')

        # Signin as second user (new client to clear session)
        client2 = APIClient()
        response2 = client2.post(
            self.signin_url,
            data={"email": "other@example.com", "password": "OtherPass123!"},
            format='json'
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['data']['user']['role'], 'employee')

    def test_signin_preserves_user_state(self):
        """Test that signin returns correct user state"""
        # Modify user state
        self.test_user.role = 'admin'
        self.test_user.save()

        signin_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!"
        }

        response = self.client.post(
            self.signin_url,
            data=signin_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['user']['role'], 'admin')
