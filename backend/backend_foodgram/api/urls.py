from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    UserViewSet, UserAvatarView, ShowSubscriptionsView, SubscribeView,
    IngredientViewSet,
    RecipeViewSet, TagViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    path('', include(router.urls)),
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'users/subscriptions/',
        ShowSubscriptionsView.as_view(),
        name='subscriptions'
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
