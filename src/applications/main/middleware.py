from django.contrib.auth import logout

class DeactivatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Make sure user is authenticated first
        if user.is_authenticated:
            # OPTION 1: Django built-in flag
            if hasattr(user, "is_active") and not user.is_active:
                logout(request)
                request.user = None  # helps avoid stale state in same request

            # OPTION 2 (uncomment if you use custom status field)
            # if hasattr(user, "status") and user.status != "active":
            #     logout(request)
            #     request.user = None

        return self.get_response(request)
        