from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Instructor_Application
from .serializers import InstructorApplicationSerializer
from users.models import User
from .serializers import ImageSerializer
from images.models import Image


from rest_framework.parsers import MultiPartParser, FormParser

class InstructorApplicationCreateWithImageAPIView(APIView):
    def post(self, request):
        
        user = request.user

        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Instructor application creation
        description = request.data.get('introduce', '')
        career = request.data.get('applicationField', '')
        # Image upload
        imagefile = request.FILES.get("image")
        
        instructor_application = Instructor_Application(user=user, description=description, career=career, image=imagefile)
        print(instructor_application)

        # If imagefile is present, update the image attribute of the instructor_application instance
        if imagefile:
            
            instructor_application.image = imagefile
            
            instructor_application.save()

        return Response(
            {"detail": "신청서가 성공적으로 생성되었습니다."}, status=status.HTTP_201_CREATED
        )
        
class InstructorApplicationListAPIView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_staff:  # 관리자가 아니면 접근할 수 없습니다
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        instructor_applications = Instructor_Application.objects.all()
        serializer = InstructorApplicationSerializer(instructor_applications, many=True)
        return Response(serializer.data)

from rest_framework.generics import ListCreateAPIView

class InstructorApplicationApprovalAPIView(APIView):
    
    
    def post(self, request):
        print(request.data)
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_staff:  # 관리자가 아니면 접근할 수 없습니다
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        applications = request.data  # 리스트로 여러 개의 신청서 데이터를 받습니다.

        for application_data in applications:
            # application_id를 사용하여 신청서를 찾습니다
            # print(id=application_data['id'])
            application = get_object_or_404(Instructor_Application, pk=application_data['id'])
                                                   
            is_done = application_data.get("isDone", None)
            # null 값은 별일 없음
            if is_done is None:
                continue
            elif is_done:
                # 강사 모델 생성 및 유저의 isInstructor를 True로 변경
                
                application.user.isInstructor = True
                application.user.save()
                print({1:application.user.instructorAbout,2:application.user.instructorCareer})

                # 강사 프로필 업데이트
                application.user.instructorAbout = application.description
                application.user.save()
                print(application.user.instructorAbout)
                
                application.user.instructorCareer = application.career
                application.user.save()
                print({1:application.user.instructorAbout,2:application.user.instructorCareer})

                
                application.delete()


            else:  # is_done이 False일 때
                application.delete()

        return Response({"detail": "신청서 처리 완료"}, status=status.HTTP_200_OK)