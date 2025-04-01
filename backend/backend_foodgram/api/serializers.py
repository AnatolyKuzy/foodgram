import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from .models import FoodgramUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = FoodgramUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'role',
            'is_subscribed', 'avatar'
        )


class UserAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField(required=True)

    def validate_avatar(self, value):
        # Проверяем, содержит ли значение avatar данные в формате base64
        if not value.startswith('data:image/'):
            raise serializers.ValidationError("Invalid image data.")
        return value

    def create_avatar(self, user):
        try:
            format, imgstr = self.validated_data['avatar'].split(';base64,')
            ext = format.split('/')[1]
            image = ContentFile(
                base64.b64decode(imgstr), name=f'user_avatar.{ext}')

            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar.save(f'user_avatar.{ext}', image, save=True)
            user.save()
        except Exception as e:
            raise serializers.ValidationError(str(e))
