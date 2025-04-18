import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'Default_key')


DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1')

ALLOWED_HOSTS = os.getenv('HOSTS', 'localhost').split(',')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'api',
    'recipes',
    'user',
]

AUTH_USER_MODEL = 'user.FoodgramUser'

DJOSER = {
    'USER_CREATE_PASSWORD_RETYPE': False,
    'LOGIN_FIELD': 'email',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserRegistrationSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user': 'api.serializers.UserSerializer',
    },
    'PERMISSIONS': {
        'current_user': ['rest_framework.permissions.IsAuthenticated'],
        'user': ['rest_framework.permissions.IsAuthenticated'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('ENGINE_DB', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DATABASE_NAME', 'foodgram'),
        'USER': os.getenv('DATABASE_USER', 'user'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'mypassword'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASS': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

MEDIA_URL = '/media/'
MEDIA_ROOT = '/media'

EMPTY = '-пусто-'
