from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status

from .models import numCart
from lectures.models import Lecture
from .serializers import CartSerializer
from lectures.serializers import LectureSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carts = numCart.objects.filter(user=request.user)
        serializer = CartSerializer(
            carts,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def put(self, request):
        cart = numCart.objects.get(user=request.user)
        lectures = request.data.get("lectures", [])

        for lecture_id in lectures:
            lecture = get_object_or_404(Lecture, pk=lecture_id)
            if lecture not in cart.lecture.all():
                cart.lecture.add(lecture)
            else:
                cart.lecture.remove(lecture)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
