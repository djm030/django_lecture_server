from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404

from rest_framework import status, exceptions, permissions
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from . import serializers
from .models import User, Activite
import jwt
import requests
import boto3
import os
import base64
import io
from PIL import Image
from django.core.files.base import ContentFile
from storages.backends.s3boto3 import S3Boto3Storage


# 유저 프로필 관련 view
class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = User.objects.get(memberId=request.user.memberId)
        serializer = serializers.OneUserSerializer(user)
        cal_lectures = user.calculatedLecture.all()

        # Get the ratings for each lecture and store them in a dictionary
        rating_dict = {}
        for cal_lec in cal_lectures:
            lecture = cal_lec.lecture
            rating_dict[lecture.lectureTitle] = lecture.rating()

        # Serialize the user and add the rating dictionary to the response data
        response_data = serializer.data.copy()
        response_data["ratings"] = rating_dict

        return Response(response_data)

    def put(self, request):
        user = request.user

        imagefile = request.FILES.get("image")

        # If there's an image file, save it
        if imagefile is not None:
            s3_storage = S3Boto3Storage()
            path = s3_storage.save("images/" + imagefile.name, imagefile)
            request.data["profileImg"] = s3_storage.url(path)
            user.profileImg = s3_storage.url(path)

        serializer = serializers.OneUserSerializer(
            user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            user = serializer.save()
            if imagefile is not None:
                user.save()
            serializer = serializers.OneUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class UserPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise exceptions.ParseError("이전 비밀번호와 새로운 비밀번호가 필요합니다.")
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# 유저 회원가입 관련 view
class UsersView(APIView):
    def post(self, request):
        password = request.data.get("password")
        # password 예외처리는 이곳
        if not password:
            raise exceptions.ParseError("password is required")

        serializer = serializers.OneUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            serializer = serializers.OneUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## username 유효성 판단
class UsernameView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        username = User.objects.filter(username=username)

        if username.exists():
            return Response("중복된 아이디 입니다.", status=status.HTTP_200_OK)
        else:
            return Response("사용해도 좋습니다.", status=status.HTTP_200_OK)


## 이메일 인증


# login
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            raise exceptions.ParseError("username or password is required")

        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        else:
            raise exceptions.ValidationError("username or password is incorrect")


# logout
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"logout": "True"})


# JWT login
class JWTokenView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            raise exceptions.ParseError()

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            # Serialize user data
            serializer = serializers.OneUserSerializer(user)
            # Get JWT tokens
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            data = {
                "user": serializer.data,
                "message": "login success",
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            }
            res = Response(data, status=status.HTTP_200_OK)

            # Set JWT tokens in cookies
            res.set_cookie(
                key="access",
                value=access_token,
                secure=True,
                httponly=True,
                samesite="None",
            )
            res.set_cookie(
                key="refresh",
                value=refresh_token,
                secure=True,
                httponly=True,
                samesite="None",
            )

            return res

        else:
            raise exceptions.ValidationError("username or password is incorrect")

    # 강사 update


class AddInstructor(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_user = User.objects.all()
        serializer = serializers.InstructorSerializer(all_user, many=True)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = serializers.InstructorSerializer(
            user,
            data=request.data,
            partial=True,
            # isInstructor =true 보내주기 요청
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.InstructorSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ActiviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.get(memberId=request.user.memberId)
        serializer = serializers.ActiviteSerializer(user)
        return Response(serializer.data)


from watchedlectures.models import WatchedLecture


class UsertempProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = User.objects.get(memberId=request.user.memberId)
        serializer = serializers.OneUserSerializer(user)
        cal_lectures = user.calculatedLecture.all()
        lecture_count = len(cal_lectures)
        is_completed_list = []
        is_completed_dict = {}
        for cal_lec in cal_lectures:
            for i in range(1, lecture_count + 1):
                try:
                    is_completed = WatchedLecture.objects.get(
                        user=user, lecture=cal_lec, lecture_num=i
                    ).is_completed
                except WatchedLecture.DoesNotExist:
                    is_completed = False
                is_completed_list.append(is_completed)
            percent = is_completed_list.count(True) / len(is_completed_list) * 100
            is_completed_dict.update({cal_lec.lecture.lectureTitle: percent})

        # Add is_completed_dict to serializer.data dictionary
        response_data = serializer.data.copy()
        response_data["is_completed_dict"] = is_completed_dict

        return Response(response_data)

    def put(self, request):
        user = request.user
        serializer = serializers.OneUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.OneUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PublicTeacher(APIView):
    def get(self, request, teacher):
        try:
            teacher_obj = User.objects.filter(name=teacher)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.AddInstructorSerializer(teacher_obj, many=True)

        return Response(serializer.data[0])


class NaverLogIn(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            client_id = "ofNjUGXrDlgmWpoZDx40"
            client_secret = "9hQKv_fPpN"

            # Get access token from code
            token_request_url = "https://nid.naver.com/oauth2.0/token"
            token_request_data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "state": "test",
                "redirect_uri": "https://cmgg.store/social/naver",
            }
            token_response = requests.post(token_request_url, data=token_request_data)
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # Get user info from access token
            profile_request_url = "https://openapi.naver.com/v1/nid/me"
            profile_response = requests.get(
                profile_request_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_data = profile_response.json()

            # Get or create user
            naver_account = profile_data.get("response")
            user, created = User.objects.get_or_create(
                username=naver_account.get("email"),
                defaults={
                    # "email" :naver_account.get("email"),
                    "name": naver_account.get("name"),
                    # "avatar": naver_account.get("profile_image"),
                },
            )

            if created:
                user.set_unusable_password()
                user.save()

            # Serialize user data
            serializer = serializers.OneUserSerializer(user)

            # Get JWT tokens
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            data = {
                "user": serializer.data,
                "message": "login success",
                "token": {"access": access_token, "refresh": refresh_token},
            }
            res = Response(data, status=status.HTTP_200_OK)

            # Set JWT tokens in cookies
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)

            return res
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class KakaoLogIn(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")

            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "0ee0a4111ed87512f2f0dfb62ebd7ae5",
                    "redirect_uri": "http://127.0.0.1:3000/social/kakao",
                    "code": code,
                },
            )

            access_token = access_token.json().get("access_token")

            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")

            # Get or create user
            user, created = User.objects.get_or_create(
                username=user_data.get("id"),
                defaults={
                    "email": kakao_account.get("email"),
                    # "name": profile.get("nickname"),
                    # "avatar": profile.get("profile_image_url"),
                },
            )

            if created:
                user.set_unusable_password()
                user.save()

            # Serialize user data
            serializer = serializers.UserSignUpSerializer(user)

            # Get JWT tokens
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            data = {
                "user": serializer.data,
                "message": "login success",
                "token": {"access": access_token, "refresh": refresh_token},
            }
            res = Response(data, status=status.HTTP_200_OK)

            # Set JWT tokens in cookies
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)

            return res

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class profileTestAPI(APIView):
    def put(self, request):
        return Response(status=status.HTTP_200_OK)


from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if refresh_token is None:
            raise InvalidToken("No refresh token provided")

        mutable_data = request.data.copy()  # Create a mutable copy
        mutable_data["refresh"] = refresh_token  # Modify the copy

        try:
            # Create a new request with the modified data
            modified_request = request._request
            modified_request.POST = mutable_data
            response = super().post(modified_request)  # Pass the modified request

        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Extract the new access token from the response data
        access_token = response.data.get("access")

        # Set the new access token as a HttpOnly cookie
        response.set_cookie("access", access_token, httponly=True)

        return response
