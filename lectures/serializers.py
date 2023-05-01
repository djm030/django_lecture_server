from rest_framework import serializers
from .models import Lecture, CalculatedLecture

from categories.serializers import CategorySerializer
from reviews.serializers import ReviewSerializer


class LectureSerializer(serializers.ModelSerializer):
    from users.serializers import (
        InstructorSerializer,
    )
    
    instructor = InstructorSerializer()
    categories = CategorySerializer()
    reviews = ReviewSerializer(many=True)
    reviews_num = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    total_student = serializers.SerializerMethodField()

    def get_reviews_num(self, object):
        return object.reviews.count()

    def get_rating(self, object):
        return object.rating()

    def get_total_student(self, object):
        return object.total_student()
    
    def to_representation(self, instance):
        reviews_queryset = instance.reviews.order_by("-id")
        reviews_serializer = ReviewSerializer(
            reviews_queryset, many=True, context={"request": self.context.get("request")}
        )
        ret = super().to_representation(instance)
        ret["reviews"] = reviews_serializer.data
        return ret
        

    class Meta:
        model = Lecture
        fields = (
            "LectureId",
            "lectureTitle",
            "lectureDifficulty",
            "lectureDescription",
            "targetAudience",
            "lectureFee",
            "thumbnail",
            "isOpened",
            "grade",
            "instructor",
            "categories",
            "reviews",
            "reviews_num",
            "rating",
            "total_student",
        )


class LectureListSerializer(serializers.ModelSerializer):
    from users.serializers import (
        InstructorSerializer,
    )

    instructor = InstructorSerializer()
    categories = CategorySerializer()
    reviews_num = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = (
            "LectureId",
            "lectureTitle",
            "lectureDifficulty",
            "lectureDescription",
            "targetAudience",
            "lectureFee",
            "thumbnail",
            "isOpened",
            "grade",
            "instructor",
            "categories",
            "reviews_num",
            "rating",
        )

    def get_rating(self, object):
        return object.rating()

    def get_reviews_num(self, object):
        return object.reviews.count()


class LectureDetailSerializer(serializers.ModelSerializer):
    lecture = LectureSerializer(read_only=True)
    total_num = serializers.SerializerMethodField()

    class Meta:
        model = CalculatedLecture
        fields = "__all__"

    def get_total_num(self, object):
        return object.total_num


class LectureTitleSerializer(serializers.ModelSerializer):
    lectureTitle = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CalculatedLecture
        fields = ("lectureTitle",)

    def get_lectureTitle(self, object):
        return object.lecture.lectureTitle


class AddLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = (
            "lectureTitle",
            "lectureDifficulty",
            
            "lectureDescription",
            "lectureFee",
            "thumbnail",
            "categories",
        )
