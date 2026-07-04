from rest_framework import serializers

class SignupSerializer(serializers.Serializer):
    firstname = serializers.CharField(
        help_text="User first name"
    )

    lastname = serializers.CharField(
        help_text="User last name"
    )

    email = serializers.EmailField(
        help_text="Email address"
    )

    password = serializers.CharField(
        write_only=True,
        help_text="Account password"
    )

    phonenumber = serializers.CharField(
        write_only=True,
        help_text="Phone number"
    )

    matricula = serializers.CharField(
        write_only=True,
        help_text="Student matricula"
    )

    terms = serializers.BooleanField(
        help_text="Must be true to create an account"
    )
