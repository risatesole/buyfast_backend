from django.db import ProgrammingError
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from api.utils import CsrfExemptSessionAuthentication
from products.default.models import Product
from ..handlers.checkout_handler_post import checkout_handler_post
from ..handlers.checkout_handler_get import checkout_handler_get
from ..handlers.checkout_handler_delete import checkout_handler_delete
from data_transfer_objects.ErrorResponse import ErrorResponse, ErrorCode


@api_view(["GET", "POST", "DELETE"])
@authentication_classes([CsrfExemptSessionAuthentication])
def checkout_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            error = ErrorResponse(
                ErrorCode.CHECKOUT_LOGIN_REQUIRED,
                "user must log in in order to checkout",
                "error",
                400
            )
            return error.http_response()

        if request.method == "GET":
            return checkout_handler_get(request)

        if request.method == "POST":
            return checkout_handler_post(request)

        if request.method == "DELETE":
            return checkout_handler_delete(request)

    except Product.DoesNotExist:
        error = ErrorResponse(
            ErrorCode.PRODUCT_DOESNT_EXISTS,
            "Product user is reaching for doesnt exists",
            "error",
            404
        )
        return error.http_response()

    except ProgrammingError:
        error = ErrorResponse(
            ErrorCode.INTERNAL_ERROR,
            "System needs configuration",
            "error",
            500
        )
        return error.http_response()

    except Exception as e:
        import traceback
        traceback.print_exc()

        error = ErrorResponse(
            ErrorCode.INTERNAL_ERROR,
            f"Unknown System error {e}",
            "error",
            500
        )
        return error.http_response()


@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
def checkout_timeslots_api_view(request):
    try:
        user = request.user

        if not user.is_authenticated:
            error = ErrorResponse(
                ErrorCode.CHECKOUT_LOGIN_REQUIRED,
                "El usuario debe iniciar sesión para consultar los horarios disponibles",
                "error",
                400
            )
            return error.http_response()

        return Response({
            "availableDates": [
                {
                    "date": "2026-06-20",
                    "slots": ["09:00", "10:00", "14:00", "17:25"]
                },
                {
                    "date": "2026-06-21",
                    "slots": ["11:00", "15:00"]
                },
                {
                    "date": "2026-06-22",
                    "slots": ["11:00", "15:00"]
                }
            ]
        })

    except ProgrammingError:
        error = ErrorResponse(
            ErrorCode.INTERNAL_ERROR,
            "El sistema necesita configuración",
            "error",
            500
        )
        return error.http_response()

    except Exception as e:
        import traceback
        traceback.print_exc()

        error = ErrorResponse(
            ErrorCode.INTERNAL_ERROR,
            f"Error desconocido del sistema: {e}",
            "error",
            500
        )
        return error.http_response()