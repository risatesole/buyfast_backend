from rest_framework import serializers
from accounts.models import User, Customer_model


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_model
        fields = ["phone", "address", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(read_only=True)
    profilepicture = serializers.CharField(source="profile_picture")
    firstname = serializers.CharField(source="first_name")
    lastname = serializers.CharField(source="last_name")
    lastLoggedIn = serializers.DateTimeField(source="updated_at")
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.status == "active"

    class Meta:
        model = User
        fields = [
            "id",
            "profilepicture",
            "firstname",
            "lastname",
            "email",
            "lastLoggedIn",
            "status",
            "role",
            "customer_profile",
        ]
