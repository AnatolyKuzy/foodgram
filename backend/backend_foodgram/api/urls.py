from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static

from .views import UserViewSet, UserAvatarView

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    path('', include(router.urls)),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)