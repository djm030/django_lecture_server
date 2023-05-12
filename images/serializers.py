from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    imagefile_url = serializers.ReadOnlyField()

    class Meta:
        model = Image
        fields = ["image"]
