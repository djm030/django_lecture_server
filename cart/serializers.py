from rest_framework import serializers
from .models import numCart
from lectures.serializers import LectureListSerializer

class CartSerializer(serializers.ModelSerializer):
    lecture = LectureListSerializer(many=True)
    class Meta:
        model = numCart
        fields = "__all__"
