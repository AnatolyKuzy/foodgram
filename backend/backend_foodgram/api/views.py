from django.shortcuts import render
import base64

from django.core.files.base import ContentFile
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import FoodgramUser
from .serializers import UserSerializer, UserAvatarSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_avatar(user)
        return Response({"avatar": user.avatar.url}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Avatar not found."}, status=status.HTTP_404_NOT_FOUND)
