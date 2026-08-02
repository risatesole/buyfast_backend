"""
Stock reduction endpoint for the `inventory` app.

Drop the pieces below into your project like this:

    inventory/serializers.py   -> ReduceStockSerializer
    inventory/views.py         -> ReduceStockView
    inventory/urls.py          -> url pattern (example at the bottom)

The view:
  1. Requires an authenticated user (request.user).
  2. Locks the product variant's most recent StockMovement row so
     concurrent sales/purchases can't race each other (select_for_update).
  3. Validates there's enough stock to remove.
  4. Creates a new StockMovement_model row with movement_type="customer_sell"
     (change this default if you also want to support other reduction reasons),
     a negative quantity, the resulting balance, and a document_reference
     that is a JSON blob with the acting user's full details.
"""

import json

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import StockMovement_model
from products.default.models import ProductVariant


# ---------------------------------------------------------------------------
# serializers.py
# ---------------------------------------------------------------------------

class ReduceStockSerializer(serializers.Serializer):
    # ProductVariant.sku is unique, so it's a safe lookup key on its own.
    sku = serializers.SlugRelatedField(
        slug_field="sku",
        queryset=ProductVariant.objects.all(),
        source="product_variant",
    )
    quantity = serializers.IntegerField(min_value=1)
    # Optional free-text note the caller can add on top of the auto-generated
    # user details (e.g. an order number). Not required.
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity to reduce must be a positive number.")
        return value


# ---------------------------------------------------------------------------
# views.py
# ---------------------------------------------------------------------------

def build_user_reference(user, note: str = "") -> str:
    """
    Builds the JSON string stored in StockMovement.document_reference,
    capturing every identifying detail of the user who performed the
    movement (name, matricula, id, role, etc).
    """
    details = {
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "matricula": user.matricula,
        "phone_number": user.phone_number,
        "role": user.role,
        "status": user.status,
        "institution_member": user.institution_member,
    }

    # Pull in role-specific details when available.
    if hasattr(user, "employee_profile"):
        details["employee"] = {
            "position": user.employee_profile.position,
            "is_active": user.employee_profile.is_active,
            "hired_at": user.employee_profile.hired_at.isoformat(),
        }
    if hasattr(user, "customer_profile"):
        details["customer"] = {
            "phone": user.customer_profile.phone,
            "address": user.customer_profile.address,
        }

    if note:
        details["note"] = note

    return json.dumps(details, default=str)


class ReduceStockView(APIView):
    """
    POST /inventory/stock/reduce/
    {
        "sku": "SHIRT-RED-M",
        "quantity": 3,
        "note": "Optional extra context, e.g. order #4821"
    }

    Requires authentication. The requesting user's full details are
    recorded on the created StockMovement row's document_reference field.
    """

    permission_classes = [IsAuthenticated]
    # Override in a subclass, or make this a serializer field, if you need
    # to support movement types other than "customer_sell" from this endpoint.
    movement_type = "customer_sell"

    def post(self, request):
        serializer = ReduceStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant = serializer.validated_data["product_variant"]
        quantity = serializer.validated_data["quantity"]
        note = serializer.validated_data["note"]

        with transaction.atomic():
            # Lock the variant's movements so two concurrent requests can't
            # both read the same starting balance.
            last_movement = (
                StockMovement_model.objects
                .select_for_update()
                .filter(product_variant=variant)
                .order_by("-date_time", "-id")
                .first()
            )
            current_balance = last_movement.balance if last_movement else 0

            if quantity > current_balance:
                return Response(
                    {
                        "detail": (
                            f"Not enough stock. Current balance is "
                            f"{current_balance}, cannot reduce by {quantity}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_balance = current_balance - quantity

            movement = StockMovement_model.objects.create(
                product_variant=variant,
                movement_type=self.movement_type,
                document_reference=build_user_reference(request.user, note),
                quantity=-quantity,  # stored negative since stock is leaving
                balance=new_balance,
            )

        return Response(
            {
                "id": movement.id,
                "product_variant": variant.id,
                "sku": variant.sku,
                "movement_type": movement.movement_type,
                "quantity": movement.quantity,
                "balance": movement.balance,
                "date_time": movement.date_time,
                "document_reference": movement.document_reference,
            },
            status=status.HTTP_201_CREATED,
        )
