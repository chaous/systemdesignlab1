Лабораторная работа 5

Данный проект представляет собой RESTful API, которое позволяет управлять пользователями и товарами, а также включает кеширование данных с помощью Redis. Основные возможности:
- Управление пользователями: регистрация, авторизация с JWT-токеном.
- Управление товарами: создание и получение данных о товарах.
- Кеширование с помощью Redis и реализация паттерна "сквозное чтение".
- Методы API: GET и POST.

Установка и запуск:

1. Клонируйте репозиторий и перейдите в директорию проекта:
git clone https://github.com/chaous/systemdesignlab1.git
cd systemdesignlab1/lab5

2. Убедитесь, что установлены Docker и Docker Compose.

3. Запустите проект:
docker-compose up --build

После запуска API будет доступно по адресу http://localhost:8000.

Эндпоинты API:

Пользователи:
1. Создание пользователя
Метод: POST /users/
Пример тела запроса:
{
    "username": "testuser",
    "password": "testpassword"
}

2. Авторизация пользователя
Метод: POST /login/
Пример тела запроса:
{
    "username": "testuser",
    "password": "testpassword"
}

3. Получение информации о пользователе
Метод: GET /users/{username}

Товары:
1. Создание товара
Метод: POST /products/
Пример тела запроса:
{
    "name": "example_product",
    "description": "example_description",
    "price": 100
}

2. Получение информации о товаре
Метод: GET /products/{product_id}

Тестирование API:

Вы можете протестировать API с помощью:
1. curl
- Создание пользователя:
curl -X POST http://localhost:8000/users/ -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
- Авторизация:
curl -X POST http://localhost:8000/login/ -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
- Создание товара:
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" -d '{"name": "example_product", "description": "example_description", "price": 100}'
- Получение товара:
curl -X GET http://localhost:8000/products/1

2. Swagger UI:
Откройте в браузере: http://localhost:8000/docs.

Состав проекта:

- main.py: Основной файл приложения.
- Dockerfile: Конфигурация сборки Docker-образа.
- docker-compose.yml: Конфигурация для запуска приложения, PostgreSQL и Redis.
- requirements.txt: Список зависимостей.

Используемые технологии:
- FastAPI: Для реализации RESTful API.
- PostgreSQL: Для хранения данных.
- Redis: Для кеширования данных.
- Docker и Docker Compose: Для контейнеризации.

Примечания:
1. Для внесения изменений в код пересоберите проект:
docker-compose up --build

2. При использовании JWT-токенов добавляйте их в заголовок запросов:
Authorization: Bearer <your_token>

Проект готов к использованию!
