from rest_framework.response import Response

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
@dataclass
class ErrorResponse:
    """
    Error codes list:
    - CHECKOUT_LOGIN_REQUIRED: the user must log in in order to checkout
    - PRODUCT_DOESNT_EXISTS: Product user is reaching for doesnt exists
    - INVALID_INPUT: invalid input data
    - RESOURCE_NOT_FOUND: requested resource not found
    - UNAUTHORIZED: authentication required
    - FORBIDDEN: insufficient permissions
    - INTERNAL_ERROR: internal server error
    """

    code: str  # e.g., "USER_NOT_FOUND", "INVALID_INPUT"
    message: str  # Human-readable error message
    status: str = "error"  # Default status string
    http_status: Optional[int] = None  # HTTP status code (optional)
    
    def __post_init__(self):
        if not self.code:
            raise ValueError("code is required")
        if not self.message:
            raise ValueError("message is required")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = {
            "code": self.code,
            "message": self.message,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
        }
        if self.http_status is not None:
            data["http_status"] = self.http_status
        if self.details:
            data["details"] = self.details
        return data
    def http_response(self):
        return Response({
                "status": self.status,
                "message": self.message, # TODO: make this none
                "data": None,
                "error":{"message":self.message,"code": self.code}
            }, status=self.http_status)


# # Usage
# error = ErrorResponse(
#     code="INVALID_EMAIL",
#     message="The provided email address is not valid",
#     status=400,
#     details={"field": "email", "value": "invalid@email"}
# )

# print(error.code)     # "INVALID_EMAIL"
# print(error.message)  # "The provided email address is not valid"
