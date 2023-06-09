from rest_framework import serializers
from .models import Review, Reply
from users.serializers import OneUserSerializer, UserNameSerializer


class ReplySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    is_same_user = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_is_same_user(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if obj.user.memberId == request.user.memberId:
                return True
            else:
                return False
        return False

    class Meta:
        model = Reply
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    reply = ReplySerializer(many=True)
    user = UserNameSerializer()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    is_same_user = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_is_same_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if obj.user.memberId == request.user.memberId:
                return True
            else:
                return False
        return False

    class Meta:
        model = Review
        exclude = (
            "title",
            "lecture",
        )


class ReviewMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ("title",)


class ReplymakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ("content",)


class ReviewmainpageSerializer(serializers.ModelSerializer):
    # reply = ReplySerializer(many=True)
    user = UserNameSerializer()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Review
        exclude = (
            "title",
            "lecture",
        )
