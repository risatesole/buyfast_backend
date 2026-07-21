# accounts/tests/test_delete_account.py
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from accounts.views.delete_account import delete_account

User = get_user_model()

class DeleteAccountTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_staff=True,
            role="employee",
            phone_number="1234567890",
            matricula="MAT001",
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

    def test_delete_account_successfully_deletes_user(self):
        """Test that authenticated user can delete their account"""
        request = self.factory.delete('/api/delete-account/')
        request = self._add_session(request, self.user)

        # Verify user exists before deletion
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

        response = delete_account(request)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'Account deleted successfully')

        # Verify user is deleted
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_account_fails_when_unauthenticated(self):
        """Test that unauthenticated user cannot delete account"""
        request = self.factory.delete('/api/delete-account/')
        request = self._add_session(request)  # No user

        response = delete_account(request)

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)

        # Verify user still exists
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_account_removes_user_from_database_completely(self):
        """Test that user is completely removed from database"""
        user_id = self.user.id
        user_email = self.user.email

        request = self.factory.delete('/api/delete-account/')
        request = self._add_session(request, self.user)

        response = delete_account(request)

        self.assertEqual(response.status_code, 200)

        # Verify user cannot be found by any field
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(User.objects.filter(email=user_email).exists())
        self.assertEqual(User.objects.count(), 0)

    def test_delete_account_does_not_affect_other_users(self):
        """Test that deleting one user doesn't affect other users"""
        # Create another user
        other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpass123",
            first_name="Jane",
            last_name="Smith",
            role="customer"
        )

        request = self.factory.delete('/api/delete-account/')
        request = self._add_session(request, self.user)

        response = delete_account(request)

        self.assertEqual(response.status_code, 200)

        # Verify other user still exists
        self.assertTrue(User.objects.filter(id=other_user.id).exists())
        self.assertEqual(User.objects.count(), 1)

    def test_delete_account_can_only_be_called_with_delete_method(self):
        """Test that only DELETE method is allowed"""
        # Test GET request
        request = self.factory.get('/api/delete-account/')
        request = self._add_session(request, self.user)

        response = delete_account(request)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        # Test POST request
        request = self.factory.post('/api/delete-account/')
        request = self._add_session(request, self.user)

        response = delete_account(request)
        self.assertEqual(response.status_code, 405)

        # Verify user still exists
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
