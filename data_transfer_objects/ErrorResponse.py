from rest_framework.response import Response

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class ErrorCode(Enum):
    """Enumeration of all possible error codes"""
    CHECKOUT_LOGIN_REQUIRED = "CHECKOUT_LOGIN_REQUIRED"
    EMPTY_BODY="EMPTY_BODY"
    PRODUCT_DOESNT_EXISTS = "PRODUCT_DOESNT_EXISTS"
    INVALID_INPUT = "INVALID_INPUT"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Additional common error codes you might want
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_REQUEST = "BAD_REQUEST"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"

    @classmethod
    def get_http_status(cls, code: 'ErrorCode') -> int:
        """Map error codes to appropriate HTTP status codes"""
        status_map = {
            cls.CHECKOUT_LOGIN_REQUIRED: 401,
            cls.PRODUCT_DOESNT_EXISTS: 404,
            cls.INVALID_INPUT: 400,
            cls.RESOURCE_NOT_FOUND: 404,
            cls.UNAUTHORIZED: 401,
            cls.FORBIDDEN: 403,
            cls.INTERNAL_ERROR: 500,
            cls.USER_NOT_FOUND: 404,
            cls.INVALID_EMAIL: 400,
            cls.INVALID_PASSWORD: 400,
            cls.DUPLICATE_ENTRY: 409,
            cls.RATE_LIMIT_EXCEEDED: 429,
            cls.SERVICE_UNAVAILABLE: 503,
            cls.BAD_REQUEST: 400,
            cls.METHOD_NOT_ALLOWED: 405,
            cls.CONFLICT: 409,
            cls.UNPROCESSABLE_ENTITY: 422,
        }
        return status_map.get(code, 500)

    @classmethod
    def get_default_message(cls, code: 'ErrorCode') -> str:
        """Get default human-readable message for each error code"""
        messages = {
            cls.CHECKOUT_LOGIN_REQUIRED: "You must be logged in to complete checkout",
            cls.PRODUCT_DOESNT_EXISTS: "The requested product does not exist",
            cls.INVALID_INPUT: "Invalid input data provided",
            cls.RESOURCE_NOT_FOUND: "The requested resource was not found",
            cls.UNAUTHORIZED: "Authentication is required to access this resource",
            cls.FORBIDDEN: "You don't have permission to perform this action",
            cls.INTERNAL_ERROR: "An internal server error occurred",
            cls.USER_NOT_FOUND: "The specified user was not found",
            cls.INVALID_EMAIL: "The provided email address is invalid",
            cls.INVALID_PASSWORD: "The provided password is incorrect",
            cls.DUPLICATE_ENTRY: "A duplicate entry already exists",
            cls.RATE_LIMIT_EXCEEDED: "Rate limit exceeded. Please try again later",
            cls.SERVICE_UNAVAILABLE: "Service is temporarily unavailable",
            cls.BAD_REQUEST: "Bad request",
            cls.METHOD_NOT_ALLOWED: "Method not allowed",
            cls.CONFLICT: "Conflict with current state of the resource",
            cls.UNPROCESSABLE_ENTITY: "The request cannot be processed",
        }
        return messages.get(code, "An error occurred")


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

    code: ErrorCode
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
                "error":{"message":self.message,"code": self.code.value}
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
