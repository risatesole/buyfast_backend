# accounts/tests/test_me_api_view.py
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from accounts.views.me_api_view import me_api_view

User = get_user_model()


class MeApiViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Create test user with all fields
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_staff=True,
            status="active",
            role="employee",
            phone_number="1234567890",
            matricula="MAT001",
            profile_picture="https://example.com/profile.jpg"
        )

    def _add_session(self, request, user=None):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        if user:
            auth_middleware = AuthenticationMiddleware(lambda req: None)
            auth_middleware.process_request(request)
            request.user = user

        return request

    def test_me_returns_correct_user_data_when_authenticated(self):
        """Test that authenticated user gets correct data"""
        request = self.factory.get('/api/me/')
        request = self._add_session(request, self.user)

        response = me_api_view(request)

        # Check status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

        # Check all user data matches
        user_data = response.data['data']['user']
        self.assertEqual(user_data['id'], self.user.id)
        self.assertEqual(user_data['firstname'], 'John')
        self.assertEqual(user_data['lastname'], 'Doe')
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['role'], 'employee')
        self.assertEqual(user_data['profilepicture'], 'https://example.com/profile.jpg')
        self.assertEqual(user_data['phone_number'], '1234567890')
        self.assertEqual(user_data['matricula'], 'MAT001')
        self.assertTrue(user_data['is_authenticated'])
        self.assertTrue(user_data['is_active'])
        self.assertTrue(user_data['is_staff'])

    def test_me_returns_null_data_when_unauthenticated(self):
        """Test that unauthenticated user gets null values"""
        request = self.factory.get('/api/me/')
        request = self._add_session(request)  # No user

        response = me_api_view(request)

        self.assertEqual(response.status_code, 200)
        user_data = response.data['data']['user']

        # All should be None/False
        self.assertIsNone(user_data['id'])
        self.assertIsNone(user_data['firstname'])
        self.assertIsNone(user_data['lastname'])
        self.assertIsNone(user_data['email'])
        self.assertIsNone(user_data['role'])
        self.assertIsNone(user_data['profilepicture'])
        self.assertFalse(user_data['is_authenticated'])
        self.assertIsNone(user_data['is_active'])
        self.assertIsNone(user_data['is_staff'])
        self.assertIsNone(user_data['phone_number'])
        self.assertIsNone(user_data['matricula'])

    def test_me_returns_correct_data_for_customer_role(self):
        """Test user with customer role"""
        customer = User.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
            role="customer",
            is_active=True,
            is_staff=False
        )

        request = self.factory.get('/api/me/')
        request = self._add_session(request, customer)

        response = me_api_view(request)

        user_data = response.data['data']['user']
        self.assertEqual(user_data['role'], 'customer')
        self.assertFalse(user_data['is_staff'])

    def test_me_returns_is_active_false_for_deactivated_user(self):
        """Test user with status deactivated"""
        self.user.status = "deactivated"
        self.user.is_active = False
        self.user.save()

        request = self.factory.get('/api/me/')
        request = self._add_session(request, self.user)

        response = me_api_view(request)

        user_data = response.data['data']['user']
        self.assertFalse(user_data['is_active'])

    def test_me_handles_missing_optional_fields(self):
        """Test user without optional fields (phone, matricula, profile_picture)"""
        minimal_user = User.objects.create_user(
            email="minimal@example.com",
            password="testpass123",
            first_name="Minimal",
            last_name="User",
            is_active=True
        )
        # These should default to None
        minimal_user.phone_number = None
        minimal_user.matricula = None
        minimal_user.profile_picture = None
        minimal_user.save()

        request = self.factory.get('/api/me/')
        request = self._add_session(request, minimal_user)

        response = me_api_view(request)

        user_data = response.data['data']['user']
        self.assertIsNone(user_data['phone_number'])
        self.assertIsNone(user_data['matricula'])
        self.assertIsNone(user_data['profilepicture'])
