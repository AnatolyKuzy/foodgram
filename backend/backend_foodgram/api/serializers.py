import base64

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile

from .models import FoodgramUser, Subscription
from recipes.models import Recipe
from recipes.serializers import ShowFavoriteSerializer


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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField(required=True)

    def validate_avatar(self, value):
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


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """ Сериализатор подписок. """

    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
            )
        ]

    def validate(self, attrs):
        """Проверяем, что пользователь не подписывается сам на себя."""
        user = attrs.get('user')
        author = attrs.get('author')

        if user == author:
            raise ValidationError("Вы не можете подписаться на себя.")

        return attrs

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data
