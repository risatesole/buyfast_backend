from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

class SandboxFormSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, help_text="Enter a test title")
    description = serializers.CharField(style={'base_template': 'textarea.html'}, required=False)
    is_active = serializers.BooleanField(default=True)

class ApiSandboxView(APIView):
    """
    API SANDBOX TESTING ENDPOINT
    ============================

    This view is a safe playground that does not touch any production data.
    You can use the HTML form below to test inputs and see how Django REST
    Framework structures the payload.
    """
    serializer_class = SandboxFormSerializer  # This automatically registers the HTML form!

    def get(self, request, *args, **kwargs):
        return Response({"message": "Use the HTML form below to submit data."})

    def post(self, request, *args, **kwargs):
        serializer = SandboxFormSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "status": "Form submitted successfully!",
                "received_data": serializer.validated_data
            })
        return Response(serializer.errors, status=400)
