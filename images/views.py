import base64
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3
import os
from images.models import Image as ImageModel


def base64_to_uploaded_file(base64_string, file_name):
    decoded_image = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(decoded_image))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return InMemoryUploadedFile(
        buffer, None, file_name, "image/png", buffer.tell(), None
    )


class UploadImageView(APIView):
    def post(self, request):
        user = request.user

        image_data = request.data.get("file")
        if not image_data:
            return Response(
                {"error": "File not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        image_data = image_data.split(",")[1]

        file_name = "uploaded_image.png"
        file = base64_to_uploaded_file(image_data, file_name)

        if file:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            file_name = default_storage.save(file.name, file)
            file_path = os.path.join(default_storage.location, file_name)

            with open(file_path, "wb") as f:
                f.write(buffer.getbuffer())

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3.upload_file(file_path, bucket_name, file_name)

            image_url = f"https://{bucket_name}.kr.object.ncloudstorage.com/{file_name}"

            image_instance = ImageModel(user=user, image=image_url)
            image_instance.save()

            return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "File not provided"}, status=status.HTTP_400_BAD_REQUEST
        )
