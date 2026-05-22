# Лабораторная работа 3

## Тема и цель

Тема лабораторной работы: `Упаковка FastAPI приложения в Docker, работа с источниками данных и очереди`.

Цель работы — упаковать уже разработанное FastAPI-приложение, базу данных и парсер данных в Docker, реализовать HTTP-вызов парсера из основного API и добавить фоновый запуск парсинга через Celery и Redis.

## Что уже было реализовано ранее

В лабораторной работе 1 было создано основное приложение `Time Manager API`:

- FastAPI-приложение;
- модели SQLModel;
- подключение к PostgreSQL;
- CRUD-эндпоинты для задач, категорий, тегов, учета времени и ежедневных планов;
- JWT-аутентификация.

В лабораторной работе 2 был создан парсер данных:

- загружает HTML-страницы документации Python;
- извлекает содержимое тега `<title>`;
- сохраняет результат в базу данных лабораторной работы 1;
- создает или обновляет задачи в таблице `Task`.

## Структура лабораторной работы 3

Код лабораторной работы находится в папке `lr_3`.

```text
lr_3/
├─ parser_service/
│  ├─ __init__.py
│  └─ main.py
├─ api.Dockerfile
├─ parser.Dockerfile
├─ docker-compose.yml
├─ requirements-api.txt
├─ requirements-parser.txt
└─ README.md
```

## HTTP-приложение парсера

Для вызова парсера по HTTP создано отдельное FastAPI-приложение `parser_service`.

Основные эндпоинты:

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/` | проверка запуска сервиса |
| `GET` | `/health` | healthcheck сервиса |
| `GET` | `/urls` | список стандартных URL из ЛР 2 |
| `POST` | `/parse` | парсинг одного URL |
| `POST` | `/parse/default` | парсинг стандартного набора URL |

Пример запроса:

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

Парсер использует общую функцию `parse_and_save_sync()` из `lr_2/task_2/parser_common.py`, поэтому результат сохраняется в ту же базу данных и в ту же таблицу `Task`.

## Вызов парсера из основного FastAPI

В основное приложение из `lr_1/lab_1` добавлен роутер `api/parser.py`.

Новый эндпоинт:

```text
POST /parser/parse
```

Он принимает URL от клиента, отправляет HTTP-запрос в отдельный контейнер `parser` и возвращает клиенту ответ parser-сервиса.

Пример запроса:

```bash
curl -X POST http://localhost:8000/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

В Docker Compose адрес parser-сервиса передается в основное приложение через переменную окружения:

```text
PARSER_API_URL=http://parser:8001
```

Имя `parser` — это имя сервиса в Docker Compose. Внутри общей Docker-сети контейнер `api` может обращаться к контейнеру парсера по этому имени.

## Вызов парсера через очередь

Для фонового запуска парсинга добавлены Celery и Redis.

Используются новые файлы:

| Файл | Назначение |
|---|---|
| `lr_1/lab_1/core/celery_app.py` | настройка Celery |
| `lr_1/lab_1/core/parser_tasks.py` | задача Celery для вызова parser API |
| `lr_1/lab_1/api/parser.py` | HTTP-эндпоинты основного API для прямого и фонового запуска |

Redis используется как брокер сообщений и backend для хранения результата задачи:

```text
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

Маршрут для постановки задачи в очередь:

```text
POST /parser/parse/async
```

Пример:

```bash
curl -X POST http://localhost:8000/parser/parse/async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/threading.html"}'
```

Ответ содержит идентификатор задачи:

```json
{
  "task_id": "...",
  "status": "queued",
  "message": "Parsing task has been added to the Celery queue"
}
```

Проверка статуса:

```bash
curl http://localhost:8000/parser/parse/tasks/<task_id>
```

Когда задача выполнится, в ответе появится результат работы парсера.

## Dockerfile основного API

Файл `api.Dockerfile` упаковывает приложение из `lr_1/lab_1`.

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY lr_3/requirements-api.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY lr_1/lab_1 /app/lr_1/lab_1

WORKDIR /app/lr_1/lab_1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile парсера

Файл `parser.Dockerfile` упаковывает отдельное FastAPI-приложение парсера и код парсера из лабораторной работы 2.

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/lr_2/task_2:/app/lr_1/lab_1:/app/lr_3

WORKDIR /app

COPY lr_3/requirements-parser.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY lr_1/lab_1 /app/lr_1/lab_1
COPY lr_2/task_2 /app/lr_2/task_2
COPY lr_3/parser_service /app/lr_3/parser_service

CMD ["uvicorn", "parser_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Docker Compose

Файл `docker-compose.yml` объединяет пять сервисов:

| Сервис | Описание |
|---|---|
| `db` | контейнер PostgreSQL |
| `api` | основное FastAPI-приложение |
| `parser` | FastAPI-приложение для вызова парсера |
| `redis` | брокер сообщений и хранилище результатов Celery |
| `celery-worker` | фоновый обработчик задач |

Основные настройки:

- `api` доступен на порту `8000`;
- `parser` доступен на порту `8001`;
- Redis доступен на порту `6379`;
- PostgreSQL внутри Docker доступен сервисам по имени `db`;
- наружу PostgreSQL проброшен на порт `5434`, чтобы не конфликтовать с локальной базой на `5432`;
- для PostgreSQL и Redis настроены `healthcheck`, а зависимые сервисы запускаются после готовности инфраструктуры.

## Запуск

Из папки лабораторной работы:

```bash
cd students/k3340/Ermakov_Makism/lr_3
docker compose up --build
```

После запуска доступны:

| Адрес | Назначение |
|---|---|
| `http://localhost:8000` | основное API |
| `http://localhost:8000/docs` | Swagger основного API |
| `http://localhost:8001` | API парсера |
| `http://localhost:8001/docs` | Swagger API парсера |

## Проверка результата

Запуск парсера:

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

Запуск парсера через основное API:

```bash
curl -X POST http://localhost:8000/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

Запуск парсера через очередь:

```bash
curl -X POST http://localhost:8000/parser/parse/async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/threading.html"}'
```

Проверка сохраненных задач через основное API:

```bash
curl http://localhost:8000/tasks/
```

Если запись уже была создана ранее, парсер обновит существующую задачу, а не создаст дубликат.

## Вывод

В результате лабораторной работы основное FastAPI-приложение, база PostgreSQL, parser API, Redis и Celery worker запускаются как единая Docker Compose-конфигурация. Парсер доступен напрямую по HTTP, интегрирован в основное API и может запускаться в фоне через очередь задач.
