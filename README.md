# Foodgram

Foodgram — это онлайн-приложение, которое позволяет пользователям делиться рецептами, составлять списки покупок и подписываться на популярных авторов.

## Основные возможности

- Создание и публикация рецептов
- Добавление рецептов в избранное
- Создание списка покупок
- Подписка на авторов
- Фильтрация рецептов по тегам и другим параметрам
- Поиск ингредиентов

## Технологии

### Backend

- Python 3.10
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- Gunicorn

## Установка и запуск проекта

### Требования

Для работы проекта вам потребуется:

- Docker
- Docker Compose

### Локальный запуск

1. Клонируйте репозиторий:

    ```
    [https://github.com/AnatolyKuzy/foodgram]
    ```
2. Создайте файл .env в корневой папке проекта:

    ```
    SECRET_KEY=<значение>
    DATABASE_NAME=<значение>
    DATABASE_USER=<значение>
    DATABASE_PASSWORD=<значение>
    DATABASE_HOST=<значение>
    DATABASE_PORT=<значение>
    ENGINE_DB=<значение>
    HOSTS=<значение>
    DEBUG=<значение>
    ```
    
3. Запустите контейнеры:

    ```
    docker-compose up -d
    ```
4. Выполните миграции:

    ```
    docker-compose exec backend python manage.py migrate
    ```

5. Создайте суперпользователя:

    ```
    docker-compose exec backend python manage.py createsuperuser
    ```
6. Соберите статические файлы:

    ```
    docker-compose exec backend python manage.py collectstatic --no-input
    ```
7. Заполните базу данных начальными данными:

    ```
    docker-compose exec backend python manage.py import_ingredients --path='/app/data/'
    ```
8. После выполнения этих шагов проект будет доступен по адресу:

    Backend: http://localhost/api/
    Frontend: http://localhost/
    Админ-панель: http://localhost/admin/
    Документация: http://localhost/api/docs/

## API Endpoints

### Рецепты

- GET /api/recipes/ - список рецептов
- GET /api/recipes/{id}/ - детали рецепта
- POST /api/recipes/ - создание рецепта
- PATCH /api/recipes/{id}/ - обновление рецепта
- DELETE /api/recipes/{id}/ - удаление рецепта

### Теги

- GET /api/tags/ - список тегов
- GET /api/tags/{id}/ - детали тега

### Ингредиенты

- GET /api/ingredients/ - список ингредиентов
- GET /api/ingredients/{id}/ - детали ингредиента

### Пользователи

- GET /api/users/ - список пользователей
- GET /api/users/{id}/ - профиль пользователя
- POST /api/users/ - регистрация
- GET /api/users/me/ - текущий пользователь

## Автор

AnatolyKuzy [GitHub](https://github.com/AnatolyKuzy/).

Проект доступен по ссылке [foodgram](http://foodgramwork.sytes.net).