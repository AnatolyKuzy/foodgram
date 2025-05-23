from django.contrib import admin

from backend_foodgram.settings import EMPTY

from user.models import Subscription, FoodgramUser


@admin.register(FoodgramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    ordering = ['username']
    empty_value_display = EMPTY


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = [
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    ]
    list_filter = ['author__username', 'user__username']
    empty_value_display = EMPTY
