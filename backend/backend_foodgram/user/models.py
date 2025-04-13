from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import UniqueConstraint


class FoodgramUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    "Use letters, '.', '@', '+', '-'."
                )
            )
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
    following = models.ManyToManyField(

        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
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


class Subscription(models.Model):

    user = models.ForeignKey(
        FoodgramUser,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        FoodgramUser,
        related_name='author',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='user_author_unique'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписался на {self.author}'
