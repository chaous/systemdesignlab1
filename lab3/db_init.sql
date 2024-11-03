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
