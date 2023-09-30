# Функциональные тесты

## Переменные окружения
Чтобы запустить тесты, нужно настроить .env по примеру из .env.example

## Запуск в docker-compose
tests/functional/docker-compose_test up --build

## Запуск тестов локально

Настроить виртуальное окружение python -m venv venv

Активация окружения venv/Scripts/activate

Запусе тестов python -m pytest .