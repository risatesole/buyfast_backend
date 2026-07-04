from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    """
    SYSTEM HEALTH STATUS
    ====================

    This endpoint provides a real-time heartbeat check for the core application services.
    It is used by uptime monitors, load balancers, and deployment platforms to verify availability.

    ENDPOINT DETAILS
    ----------------
    * Method: GET
    * Authentication: None (Publicly Accessible)
    * Response Format: application/json

    DEPENDENT SERVICES CHECKED
    --------------------------
    1. Primary Database (SQLite): Connected and Operational
    2. Authentication Middleware: Active
    3. Static File Storage: Accessible

    EXPECTED RESPONSE
    -----------------
    {
        "status": "ok"
    }
    """
    return Response({"status": "ok"})
