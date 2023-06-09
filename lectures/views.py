from rest_framework.views import APIView
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from .models import Lecture, CalculatedLecture
from . import serializers
from rest_framework import permissions, status
from categories.models import Category
from categories.serializers import CategorySerializer
from django.conf import settings
from users.models import User
from videos.models import Video
from videos.serializers import VideoListSerializer


#
class Lectures(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        # Get search query from query params
        try:
            search_query = request.query_params.get("search", "")
        except:
            search_query = ""

        # settings 로 보낼것.
        print(search_query)
        page_size = 24
        start = (page - 1) * page_size
        end = start + page_size
        lectures = Lecture.objects.filter(lectureTitle__icontains=search_query)
        total_num = lectures.count()
        lectures = lectures[start:end]
        print(total_num)
        serializer = serializers.LectureListSerializer(lectures, many=True)

        return Response({"data": serializer.data, "totalNum": total_num})

    def post(self, request):
        if request.user.isInstructor:
            serializer = serializers.LectureListSerializer(data=request.data)
            if serializer.is_valid():
                lecture = serializer.save()
                serializer = serializers.LectureListSerializer(lecture)
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        else:
            raise ParseError()


class LecturesDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Lecture.objects.get(LectureId=pk)
        except Lecture.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        lecture = self.get_object(pk)
        cal_lec = CalculatedLecture.objects.get(lecture=lecture)
        video_list = Video.objects.filter(calculatedLecture=cal_lec)
        is_enrolled = False
        # 유저가 해당 강의를 수강중인지 확인
        try:
            user = User.objects.get(memberId=request.user.memberId)
            if cal_lec in user.calculatedLecture.all():
                is_enrolled = True
        except:
            pass
        video_serializer = VideoListSerializer(video_list, many=True)
        serializer = serializers.LectureSerializer(
            lecture, context={"request": request}
        )
        return Response(
            {
                "lecture_data": serializer.data,
                "video_data": video_serializer.data,
                "is_enrolled": is_enrolled,
            }
        )

    def put(self, request, pk):
        lecture = self.get_object(pk)
        serializer = serializers.LectureListSerializer(
            lecture,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_lecture = serializer.save()
            return Response(
                serializers.LectureListSerializer(updated_lecture).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk)
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class SearchLectures(APIView):
    def get(self, request):
        # Filter by search words
        search_words = request.query_params.get("s", "")
        user = User.objects.get(name__icontains=search_words)
        if search_words:
            lectures = Lecture.objects.filter(
                lectureTitle__icontains=search_words
            ) or Lecture.objects.filter(lectureTitle__icontains=search_words)
        else:
            lectures = Lecture.objects.all()
        # Apply category filter if specified
        # Paginate results
        total_num = lectures.count()
        page_size = 24
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size
        paged_lectures = lectures[start:end]
        # Serialize results
        serializer = serializers.LectureListSerializer(paged_lectures, many=True)
        return Response({"data": serializer.data, "totalNum": total_num})


class OneCategory(APIView):
    def get_CategoryObject(self, category1):
        try:
            category = Category.objects.get(classification=category1)
            return Category.objects.filter(parent=category)
        except Category.DoesNotExist:
            raise NotFound

    def get(self, request, category1):
        # Get child categories of specified category
        categories = self.get_CategoryObject(category1)
        # Get search query from query parameters
        search_query = request.query_params.get("search", "")
        # Get all lectures that belong to any of the child categories
        union_query = None
        for category in categories:
            lectures = Lecture.objects.filter(categories=category)
            # Filter the lectures based on search query
            if search_query:
                lectures = lectures.filter(lectureTitle__icontains=search_query)
            if union_query is None:
                union_query = lectures
            else:
                union_query = union_query.union(lectures)
        # Count the total number of lectures
        total_num = union_query.count()
        # Get page number from query parameters
        page = int(request.query_params.get("page", 1))
        # Set page size and calculate start and end indices
        page_size = 24
        start = (page - 1) * page_size
        end = start + page_size
        # Slice the data based on start and end indices
        paged_union_query = union_query[start:end]
        # Serialize results
        serializer = serializers.LectureListSerializer(paged_union_query, many=True)
        # Construct the response
        return Response({"data": serializer.data, "totalNum": total_num})


class OneCategoryPage(APIView):
    def get_CategoryObject(self, category1):
        try:
            category = Category.objects.get(classification=category1)
            return Category.objects.filter(parent=category)
        except Category.DoesNotExist:
            raise NotFound

    def get(self, request, category1, pages):
        # Get child categories of specified category
        categories = self.get_CategoryObject(category1)
        # Get search query from query parameters
        search_query = request.query_params.get("search", "")
        # Get all lectures that belong to any of the child categories
        union_query = None
        for category in categories:
            lectures = Lecture.objects.filter(categories=category)
            # Filter the lectures based on search query
            if search_query:
                lectures = lectures.filter(lectureTitle__icontains=search_query)
            if union_query is None:
                union_query = lectures
            else:
                union_query = union_query.union(lectures)
        # Count the total number of lectures
        total_num = union_query.count()
        # Set page size and calculate start and end indices
        page_size = 24
        start = (pages - 1) * page_size
        end = start + page_size
        # Slice the data based on start and end indices
        paged_union_query = union_query[start:end]
        # Serialize results
        serializer = serializers.LectureListSerializer(paged_union_query, many=True)
        # Construct the response
        return Response({"data": serializer.data, "totalNum": total_num})


class TwoCategory(APIView):
    def get_CategoryObject(self, category2):
        try:
            return Category.objects.get(classification=category2)
        except Category.DoesNotExist:
            raise NotFound

    def get(self, request, category1, category2):
        # Get category object from database
        category = self.get_CategoryObject(category2)
        # Get search query from query parameters
        search_query = request.query_params.get("search", "")
        # Get lectures that belong to the specified category
        lectures = Lecture.objects.filter(categories=category)
        # Filter the lectures based on search query
        if search_query:
            lectures = lectures.filter(lectureTitle__icontains=search_query)
        # Count the total number of lectures
        total_num = lectures.count()
        # Set page size and calculate start and end indices
        page_size = 24
        page = int(request.query_params.get("page", 1))
        start = (page - 1) * page_size
        end = start + page_size
        # Slice the data based on start and end indices
        paged_lectures = lectures[start:end]
        # Serialize results
        serializer = serializers.LectureListSerializer(paged_lectures, many=True)
        # Construct the response
        return Response({"data": serializer.data, "totalNum": total_num})


class TwoCategoryPage(APIView):
    def get_CategoryObject(self, category2):
        try:
            return Category.objects.get(classification=category2)
        except Category.DoesNotExist:
            raise NotFound

    def get(self, request, category1, category2, pages):
        # Get category object from database
        category = self.get_CategoryObject(category2)
        # Get search query from query parameters
        search_query = request.query_params.get("search", "")
        # Get lectures that belong to the specified category
        lectures = Lecture.objects.filter(categories=category)
        # Filter the lectures based on search query
        if search_query:
            lectures = lectures.filter(lectureTitle__icontains=search_query)
        # Count the total number of lectures
        total_num = lectures.count()
        # Set page size and calculate start and end indices
        page_size = 24
        start = (pages - 1) * page_size
        end = start + page_size
        # Slice the data based on start and end indices
        paged_lectures = lectures[start:end]
        # Serialize results
        serializer = serializers.LectureListSerializer(paged_lectures, many=True)
        # Construct the response
        return Response({"data": serializer.data, "totalNum": total_num})


class InstructorName(APIView):
    def get(self, request, username):
        # print("username", username)
        try:
            user = User.objects.get(username=username)

            user_lecture = Lecture.objects.filter(instructor=user)
        except Lecture.DoesNotExist:
            raise NotFound
        serializer = serializers.LectureDetailSerializer(user_lecture, many=True)
        return Response(serializer.data)


from django.db.models import Count
from reviews.models import Review
from reviews.serializers import ReviewmainpageSerializer


class MainPage(APIView):
    def get(self, request):
        top_lectures = Lecture.objects.annotate(
            total_students=Count("calculatedlecture__user")
        ).order_by("-total_students")[:8]
        top_lectures_serializer = serializers.LectureListSerializer(
            top_lectures, many=True
        )

        all_review = Review.objects.filter(rating__gte=4)[:4]
        review_serializer = ReviewmainpageSerializer(all_review, many=True)

        return Response(
            {
                "carousel": top_lectures_serializer.data,
                "review": review_serializer.data,
            }
        )


class addLecture(APIView):
    def post(self, request):
        try:
            serializer = serializers.AddLectureSerializer(data=request.data)
            user = User.objects.get(username=request.user)
            if serializer.is_valid():
                lecture = serializer.save(
                    instructor=user,
                    categories=Category.objects.get(name="뷰"),
                    targetAudience=request.data["lectureDifficulty"],
                )
                serializer = serializers.AddLectureSerializer(lecture)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from django.db.models import Min, Max


class errortest(APIView):
    def get(self, request):
        lectures = Lecture.objects.all()
        min_lecture_id = lectures.aggregate(Min("LectureId"))["LectureId__min"]
        max_lecture_id = lectures.aggregate(Max("LectureId"))["LectureId__max"]
        for lecture_id in range(min_lecture_id, max_lecture_id):
            # Lecture 모델에서 LectureId에 해당하는 객체를 가져옵니다.
            lecture = Lecture.objects.get(LectureId=lecture_id)

            # lecture 객체와 연결된 모든 CalculatedLecture 객체를 가져옵니다.
            calculated_lectures = CalculatedLecture.objects.filter(lecture=lecture)

            # 중복된 CalculatedLecture 객체들을 삭제합니다. (하나를 제외한 나머지 객체들을 삭제합니다.)
            calculated_lectures.exclude(pk=calculated_lectures.first().pk).delete()
        return Response(status=status.HTTP_200_OK)


class SearchEngine(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        1. 검색어
        2. 카테고리
        3. 난이도
        4. 정렬
        """

        ## 검색어
        try:
            search_query = request.query_params.get("search", "")
        except:
            search_query = ""

        ## 카테고리
        try:
            category_query = request.query_params.get("category", "")
        except:
            category_query = ""
        category_list = category_query.split(",")

        ## 난이도
        try:
            level_query = request.query_params.get("level", "1,2,3,4")
        except:
            level_query = "1,2,3,4"
        level_list = level_query.split(",")
        level_dict = {"1": "beginner", "2": "easy", "3": "middle", "4": "hard"}
        level_list = [level_dict.get(level) for level in level_list]

        ## 정렬
        try:
            sort_by_query = request.query_params.get("sort_by", "latest")
        except:
            sort_by_query = "latest"

        ## 오름차순 내림차순
        try:
            order_query = request.query_params.get("order", "asc")
        except:
            order_query = "asc"
        if order_query == "desc":
            sort_by_query = "-" + sort_by_query

        ## pagination
        try:
            page = request.query_params.get("page", 1)
        except:
            page = 1
        try:
            page = int(page)
        except ValueError:
            page = 1

        # 강의 검색
        lectures = Lecture.objects.all()

        if search_query:
            lectures = lectures.filter(lectureTitle__icontains=search_query)
        if category_list[0]:
            lectures = lectures.filter(category__in=category_list)
        if level_list[0]:
            lectures = lectures.filter(level__in=level_list)

        lectures = lectures.order_by(sort_by_query)

        page_size = 24
        start = (page - 1) * page_size
        end = start + page_size
        total_num = lectures.count()
        lectures = lectures[start:end]
        serializer = serializers.LectureListSerializer(lectures, many=True)

        return Response({"data": serializer.data, "totalNum": total_num})
