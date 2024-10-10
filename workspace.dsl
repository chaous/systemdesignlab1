workspace {
    name "Project Management System"
    description "Архитектура системы для управления проектами, задачами и пользователями"

    !identifiers hierarchical

    model {
        user = person "Пользователь" {
            description "Использует систему для управления проектами и задачами"
        }

        pmSystem = softwareSystem "Project Management System" {
            description "Система для управления проектами, задачами и пользователями"

            userDb = container "User Database" {
                technology "PostgreSQL"
                description "Хранит данные о пользователях"
            }

            projectDb = container "Project Database" {
                technology "PostgreSQL"
                description "Хранит данные о проектах"
            }

            taskDb = container "Task Database" {
                technology "PostgreSQL"
                description "Хранит данные о задачах"
            }

            webApp = container "Web Application" {
                technology "React, JavaScript"
                description "Веб-приложение для взаимодействия с пользователями"
            }

            apiGateway = container "API Gateway" {
                technology "Spring Cloud Gateway"
                description "Маршрутизирует запросы от клиентов"
            }

            userService = container "User Service" {
                technology "Java Spring Boot"
                description "Сервис для управления пользователями"
                -> apiGateway "Запросы на управление пользователями" "HTTPS"
                -> userDb "Читает и записывает данные о пользователях" "JDBC"
            }

            projectService = container "Project Service" {
                technology "Java Spring Boot"
                description "Сервис для управления проектами"
                -> apiGateway "Запросы на управление проектами" "HTTPS"
                -> projectDb "Читает и записывает данные о проектах" "JDBC"
            }

            taskService = container "Task Service" {
                technology "Java Spring Boot"
                description "Сервис для управления задачами"
                -> apiGateway "Запросы на управление задачами" "HTTPS"
                -> taskDb "Читает и записывает данные о задачах" "JDBC"
            }
        }

        user -> pmSystem.webApp "Взаимодействует через веб-приложение"
        pmSystem.webApp -> pmSystem.apiGateway "Передает запросы" "HTTPS"
    }

    views {
        systemContext pmSystem {
            include *
            autolayout lr
        }

        container pmSystem {
            include *
            autolayout lr
        }

        dynamic pmSystem "createTask" "Создание задачи в проекте" {
            user -> pmSystem.webApp "Создает задачу в проекте"
            pmSystem.webApp -> pmSystem.apiGateway "POST /task"
            pmSystem.apiGateway -> pmSystem.taskService "Создает запись задачи"
            pmSystem.taskService -> pmSystem.taskDb "INSERT INTO tasks"
            autolayout lr
        }

        dynamic pmSystem "createUser" "Создание нового пользователя" {
            user -> pmSystem.webApp "Создание нового пользователя"
            pmSystem.webApp -> pmSystem.apiGateway "POST /user"
            pmSystem.apiGateway -> pmSystem.userService "Создает запись о пользователе"
            pmSystem.userService -> pmSystem.userDb "INSERT INTO users"
            autolayout lr
        }

        dynamic pmSystem "findProjectByName" "Поиск проекта по имени" {
            user -> pmSystem.webApp "Поиск проекта по имени"
            pmSystem.webApp -> pmSystem.apiGateway "GET /project?name={projectName}"
            pmSystem.apiGateway -> pmSystem.projectService "Ищет проект в базе данных"
            pmSystem.projectService -> pmSystem.projectDb "SELECT * FROM projects WHERE name={projectName}"
            autolayout lr
        }

        theme default
    }
}
