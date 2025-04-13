import base64

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField

from user.models import FoodgramUser, Subscription
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = FoodgramUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = FoodgramUser
        fields = (
            'email', 'id', 'avatar', 'is_subscribed',
            'username', 'first_name', 'last_name'
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


class ShowFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShowSubscriptionsSerializer(serializers.ModelSerializer):

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientWithAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = IngredientWithAmountSerializer(
        many=True,
        required=True,
        source='recipeingredient_set'
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, required=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'ingredients', 'tags', 'cooking_time',
                  'author', 'image', 'is_favorited', 'is_in_shopping_cart')
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        """Метод для проверки наличия рецепта в избранном."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Метод для проверки наличия рецепта в списке покупок."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'ingredients', 'tags', 'cooking_time', 'image')
        read_only_fields = ('author',)

    @transaction.atomic
    def create(self, validated_data):
        """Метод для создания рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipeingredient_set.all().delete()
            recipe_ingredients = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод для представления рецепта."""
        return RecipeSerializer(instance, context=self.context).data

    def validate(self, data):
        """Метод для проверки валидности данных."""
        author = self.context['request'].user
        name = data.get('name')

        if Recipe.objects.filter(author=author, name=name).exists():
            raise serializers.ValidationError({
                'name': 'У вас уже есть рецепт с таким названием'
            })

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег'
            })

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Теги должны быть уникальными'
            })

        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужно выбрать хотя бы один ингредиент'
            })

        ingredients_ids = []
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient'].id
            if not ingredient_id:
                raise serializers.ValidationError({
                    'ingredients': 'Отсутствует id ингредиента'
                })
            ingredients_ids.append(ingredient_id)

        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться'
            })

        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data
