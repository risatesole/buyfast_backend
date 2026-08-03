from mediaupload.uploader import upload_file
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication


class AvatarUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def avatar_upload_api_view(request):
    serializer = AvatarUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    url = upload_file(serializer.validated_data["file"])

    user = request.user
    user.profile_picture = url
    user.save()

    return Response(
        {"url": url},
        status=status.HTTP_201_CREATED,
    )
