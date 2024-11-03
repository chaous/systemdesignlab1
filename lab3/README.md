# Лабораторная работа №3

## Описание

Этот проект представляет собой сервис управления проектами и задачами с поддержкой управления пользователями. Он реализован с использованием FastAPI и хранит данные в базе данных PostgreSQL. В проекте предусмотрена аутентификация с использованием JWT-токенов и работа с CRUD-операциями для пользователей, проектов и задач.

### Основной функционал:
- **JWT-аутентификация**: защищенные маршруты требуют авторизации пользователя с использованием токена.
- **CRUD операции для пользователей, проектов и задач**.
- **Хранение данных в PostgreSQL** с использованием SQLAlchemy для работы с базой данных.

### Мастер-пользователь для тестирования:
- Логин: `admin`
- Пароль: `secret`

---

## Установка и настройка

### Предварительные шаги
1. Убедитесь, что PostgreSQL установлен и запущен на вашем компьютере.
2. Создайте базу данных `project_management`:
   ```sql
   CREATE DATABASE project_management;
   ```

### Клонирование репозитория и настройка окружения
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/chaous/systemdesignlab1.git
   cd lab3
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Для Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Настройка базы данных
1. Обновите `DATABASE_URL` в файле `main.py` с вашими учетными данными PostgreSQL:
   ```python
   DATABASE_URL = "postgresql://<user>:<password>@localhost/project_management"
   ```
   - `<user>`: Имя пользователя базы данных (например, `postgres`).
   - `<password>`: Пароль пользователя PostgreSQL.

2. Запустите скрипт инициализации базы данных (`db_init.sql`) для создания таблиц и добавления тестовых данных:
   ```sql
   -- Создание таблицы пользователей
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       username VARCHAR(50) UNIQUE NOT NULL,
       full_name VARCHAR(100),
       email VARCHAR(100) UNIQUE NOT NULL,
       password VARCHAR(100) NOT NULL
   );

   -- Индекс по полю username для быстрого поиска
   CREATE INDEX idx_users_username ON users(username);

   -- Создание таблицы проектов
   CREATE TABLE projects (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100) UNIQUE NOT NULL,
       description TEXT,
       owner_id INTEGER REFERENCES users(id)
   );

   -- Индекс по полю name для быстрого поиска
   CREATE INDEX idx_projects_name ON projects(name);

   -- Создание таблицы задач
   CREATE TABLE tasks (
       id SERIAL PRIMARY KEY,
       title VARCHAR(100) NOT NULL,
       description TEXT,
       project_id INTEGER REFERENCES projects(id),
       assigned_to INTEGER REFERENCES users(id)
   );

   -- Добавление тестовых данных
   INSERT INTO users (username, full_name, email, password)
   VALUES ('admin', 'Administrator', 'admin@example.com', 'hashed_secret');
   ```

### Запуск сервиса
1. Запустите FastAPI:
   ```bash
   uvicorn main:app --reload
   ```

2. Откройте браузер и перейдите по ссылке:
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) для просмотра и тестирования API.

---

## Решение проблем с подключением к PostgreSQL

Если вы получаете ошибку `connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused`, выполните следующие шаги:

1. **Убедитесь, что PostgreSQL запущен**:
   - На MacOS с Homebrew можно запустить PostgreSQL командой:
     ```bash
     brew services start postgresql
     ```
   - Для других операционных систем используйте команду запуска PostgreSQL в зависимости от способа установки.

2. **Проверьте параметры подключения** в `main.py`, убедившись, что они верны:
   ```python
   DATABASE_URL = "postgresql://<user>:<password>@localhost/project_management"
   ```

3. **Проверьте, создана ли база данных**:
   - Подключитесь к PostgreSQL:
     ```bash
     psql -U <user>
     ```
   - Создайте базу данных `project_management`, если её нет:
     ```sql
     CREATE DATABASE project_management;
     ```

После выполнения этих шагов перезапустите сервер FastAPI командой:
```bash
uvicorn main:app --reload
```

---

## JWT Аутентификация

Для использования защищенных маршрутов требуется аутентификация через JWT. Для этого нужно пройти аутентификацию и получить токен, который будет использоваться в запросах.

### Получение токена
- **POST /token**: Аутентификация и получение JWT-токена.

Пример запроса:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=secret'
```

Токен будет использоваться для аутентификации в других запросах через заголовок:
```bash
-H "Authorization: Bearer <JWT_TOKEN>"
```

---

## API Маршруты

### Управление пользователями
- **POST /users/** - Создание нового пользователя.
- **GET /users/{username}** - Получение пользователя по логину.

Пример создания пользователя:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/users/' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "newuser",
    "full_name": "New User",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

### Управление проектами
- **POST /projects/** - Создание нового проекта.
- **GET /projects/{project_name}** - Поиск проекта по имени.

Пример создания проекта:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/projects/' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Project A",
    "description": "Описание проекта A",
    "owner": "admin"
  }'
```

### Управление задачами
- **POST /tasks/** - Создание новой задачи.
- **GET /projects/{project_name}/tasks/** - Получение всех задач проекта.

Пример создания задачи:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/tasks/' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Task 1",
    "description": "Описание задачи 1",
    "project": "Project A",
    "assigned_to": "admin"
  }'
```

---

## Нефункциональные требования

1. **Производительность**: 
   - Все запросы должны выполняться в течение 2 секунд.
  
2. **Безопасность**: 
   - Доступ к защищенным маршрутам возможен только при наличии JWT-токена.

3. **Надежность**: 
   - Система поддерживает минимальную потерю данных благодаря использованию базы данных PostgreSQL.

4. **Масштабируемость**: 
   - Система легко масштабируется для больших объемов данных благодаря поддержке реляционной базы данных.

---

## Автор

Илья Рожков

---
