from rest_framework.authentication import SessionAuthentication

# Django REST Framework enforces CSRF checks on session-authenticated requests by default.
# This subclass disables that behaviour, which is useful for API endpoints that are
# accessed programmatically (e.g. mobile apps, Postman, or other services) where
# sending a CSRF token is not practical. Authentication and permissions still apply —
# only the CSRF check is bypassed.
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # skip CSRF check