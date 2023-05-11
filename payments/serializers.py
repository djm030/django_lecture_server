from rest_framework import serializers
from .models import Payment
from lectures.serializers import LectureSerializer


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    lectures = LectureSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "lectures",
            "payment_date",
        )
