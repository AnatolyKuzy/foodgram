from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class FoodgramUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+$', message="Username must be alphanumeric or contain '.', '@', '+', '-'.")
        ],
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="Email"
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    role = models.CharField(
        max_length=10,
        choices=[
            ('user', 'Пользователь'),
            ('admin', 'Администратор'),
            ('moderator', 'Модератор')
        ],
        default='user',
        verbose_name="Роль"
    )
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to="media/users",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def is_admin(self):
        return self.role == 'admin' or self.is_staff

    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username[:50]
