# orders/views/admin/serializer.py
from rest_framework import serializers
from orders.models import Order


class OrderListSerializer(serializers.ModelSerializer):
    """
    Administrative serializer for the orders list endpoint.
    Shapes output to match the frontend contract exactly:
    id, profilepicture, firstname, lastname, email, created_at, total, status, pickup_time
    """

    id = serializers.SerializerMethodField()
    profilepicture = serializers.SerializerMethodField()
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    pickup_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "profilepicture",
            "firstname",
            "lastname",
            "email",
            "created_at",
            "total",
            "status",
            "pickup_time",
        ]

    def get_id(self, obj):
        return obj.pk

    # --- customer fields ---
    def get_profilepicture(self, obj):
        customer = getattr(obj, "customer", None)
        if not customer:
            return None
        # ADJUST: match whatever field actually holds the avatar URL on User
        for attr in ("profile_picture", "profilepicture", "avatar", "photo_url"):
            val = getattr(customer, attr, None)
            if val:
                return val.url if hasattr(val, "url") else val
        return None

    def get_firstname(self, obj):
        customer = getattr(obj, "customer", None)
        return getattr(customer, "first_name", None) if customer else None

    def get_lastname(self, obj):
        customer = getattr(obj, "customer", None)
        return getattr(customer, "last_name", None) if customer else None

    def get_email(self, obj):
        customer = getattr(obj, "customer", None)
        return getattr(customer, "email", None) if customer else None

    # --- total: subtotal + tax from the view's annotated queryset, matching
    # what the customer was actually charged (OrderItem.subtotal semantics) ---
    def get_total(self, obj):
        # total_amount/total_tax come from the .annotate(...) in the view.
        # Falls back to 0 if the serializer is ever used without that annotation.
        return getattr(obj, "total_amount", 0) + getattr(obj, "total_tax", 0)

    # --- datetimes: ISO-8601 with milliseconds + "Z", matching the JS Date
    # .toISOString() format the frontend expects (e.g. 2026-05-04T23:51:25.203Z) ---
    def _format_dt(self, value):
        if not value:
            return None
        return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"

    def get_created_at(self, obj):
        return self._format_dt(obj.created_at)

    def get_pickup_time(self, obj):
        return self._format_dt(obj.pickup_time)