from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from user.models import FoodgramUser, Subscription
from .serializers import (
    UserSerializer, UserAvatarSerializer,
    SubscriptionSerializer, ShowSubscriptionsSerializer, FavoriteSerializer,
    IngredientSerializer, RecipeSerializer,
    TagSerializer, RecipeShortSerializer,
    RecipeCreateUpdateSerializer,
)
from .pagination import CustomPagination


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получение данных текущего пользователя."""
        return super().me(request)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def get_object(self):
        return self.request.user


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


class SubscribeView(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(FoodgramUser, id=id)
        if request.user.follower.filter(author=author).exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):

    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        queryset = FoodgramUser.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteView(APIView):

    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if request.user.favorites.filter(recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже добавлен в избранное.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favorite = request.user.favorites.filter(recipe=recipe).first()
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт не в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('name', 'author__username', 'tags__name')
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """Метод для добавления и удаления рецепта из списка избранного."""
        recipe = self.get_object()
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, recipe.id)
        return self.remove_from(Favorite, request.user, recipe.id)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Метод для добавления и удаления рецепта из списка покупок."""
        recipe = self.get_object()
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, recipe.id)
        return self.remove_from(ShoppingCart, request.user, recipe.id)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, *args, **kwargs):
        """Метод для получения короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        short_link = f'{request.get_host()}/{recipe.short_link}/'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='short-link-redirect',
    )
    def short_link_redirect(self, request, short_link=None):
        """Перенаправление по короткой ссылке на рецепт."""
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return HttpResponseRedirect(f'/recipes/{recipe.pk}/')

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""
        ingredients = (
            Recipe.objects.filter(in_shopping_cart__user=request.user)
            .values(
                'ingredients__name',
                'ingredients__measurement_unit'
            )
            .annotate(total_amount=Sum('recipeingredient__amount'))
            .order_by('ingredients__name')
        )

        shopping_list = ['Список покупок:\n\n']
        for ingredient in ingredients:
            shopping_list.append(
                f"- {ingredient['ingredients__name']} "
                f"({ingredient['ingredients__measurement_unit']}) — "
                f"{ingredient['total_amount']}\n"
            )

        response = HttpResponse(
            ''.join(shopping_list),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def get_permissions(self):
        """Метод для проверки прав доступа."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdminOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Метод для сохранения рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод для получения сериализатора."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return super().get_serializer_class()

    def add_to(self, model, user, pk):
        """Метод для проверки существования объекта и создания нового."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'detail': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(
            recipe, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from(self, model, user, pk):
        """Метод для удаления объекта."""
        try:
            obj = get_object_or_404(model, user=user, recipe__id=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    ingredient_lines = [
        f"{ingredient_data['ingredient__name']} - "
        f"{ingredient_data['amount']} "
        f"{ingredient_data['ingredient__measurement_unit']}"
        for ingredient_data in ingredients
    ]

    ingredient_list = "Cписок покупок:\n" + "\n".join(ingredient_lines)
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
