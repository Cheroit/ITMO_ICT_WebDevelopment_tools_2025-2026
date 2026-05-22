# Лабораторная работа 3

## Назначение

В этой лабораторной работе FastAPI-приложение из `lr_1/lab_1`, база данных PostgreSQL и парсер из `lr_2/task_2` упакованы в Docker.

Состав сервисов:

| Сервис | Назначение | Порт |
|---|---|---:|
| `api` | основное приложение Time Manager API | `8000` |
| `parser` | отдельное FastAPI-приложение для запуска парсера по HTTP | `8001` |
| `db` | PostgreSQL для основного API и парсера | `5434` |
| `redis` | брокер сообщений и хранилище результатов Celery | `6379` |
| `celery-worker` | фоновый обработчик задач парсинга | - |

## Запуск

```bash
cd students/k3340/Ermakov_Makism/lr_3
docker compose up --build
```

После запуска:

- основное API доступно по адресу `http://localhost:8000`;
- API парсера доступно по адресу `http://localhost:8001`;
- документация основного API: `http://localhost:8000/docs`;
- документация парсера: `http://localhost:8001/docs`.

## Проверка парсера

Запуск парсинга одного URL напрямую через parser API:

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

Запуск парсинга через основное API, которое само отправляет запрос в контейнер `parser`:

```bash
curl -X POST http://localhost:8000/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/asyncio.html"}'
```

Запуск парсинга через очередь Celery:

```bash
curl -X POST http://localhost:8000/parser/parse/async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.python.org/3/library/threading.html"}'
```

Ответ содержит `task_id`. По нему можно проверить состояние задачи:

```bash
curl http://localhost:8000/parser/parse/tasks/<task_id>
```

Запуск парсинга стандартного набора URL из лабораторной работы 2:

```bash
curl -X POST http://localhost:8001/parse/default
```

Результат сохраняется в таблицу `Task` основной базы данных. Проверить созданные задачи можно через основное API:

```bash
curl http://localhost:8000/tasks/
```
