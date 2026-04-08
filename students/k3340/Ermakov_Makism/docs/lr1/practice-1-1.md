# Практическая работа 1.1

## Тема работы

Практика посвящена созданию самого простого FastAPI-приложения, запуску `uvicorn`, работе с временной базой данных и использованию `Pydantic`-моделей для типизации и валидации.

## Что требовалось по заданию

По методическим указаниям нужно было:

- создать базовое приложение FastAPI;
- реализовать корневой маршрут `GET /`;
- создать временную базу данных для главной таблицы;
- сделать так, чтобы главная запись содержала один вложенный объект и список вложенных объектов;
- реализовать CRUD для главной сущности;
- описать Pydantic-модели;
- сделать модели и API для вложенного объекта.

## Структура практики

Практическая работа выполнена в папке `lr_1/practice_1_1` и состоит из двух основных файлов:

- `main.py` — маршруты и временная база данных;
- `models.py` — Pydantic-модели.

## Шаг 1. Создание базового приложения

В начале был создан объект приложения `FastAPI` и добавлен корневой маршрут:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello() -> str:
    return "Hello, Maksim!"
```

Этот обработчик нужен для самой первой проверки, что приложение успешно запускается через:

```bash
uvicorn main:app --reload
```

После запуска можно открыть:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Шаг 2. Создание временной базы данных

Вместо настоящей СУБД на первом этапе использовался список словарей `temp_bd`. В него были добавлены две записи, каждая из которых содержит:

- поле `id`;
- поля с основной информацией о воине;
- вложенный объект `profession`;
- список объектов `skills`.

Ключевой фрагмент:

```python
temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам"
        },
        "skills": [
            {
                "id": 1,
                "name": "Купле-продажа компрессоров",
                "description": ""
            },
            {
                "id": 2,
                "name": "Оценка имущества",
                "description": ""
            }
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 2,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    }
]
```

Так была выполнена ключевая часть задания: у главной сущности есть и одиночный вложенный объект, и список объектов.

## Шаг 3. Описание моделей данных через Pydantic

Для типизации были реализованы модели `Profession`, `Skill` и `Warrior`, а также перечисление `RaceType`.

Основной код:

```python
class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
```

Эти модели сделали проект лучше сразу в нескольких отношениях:

- появилась валидация входных данных;
- документация Swagger стала показывать структуры запросов и ответов;
- поле `race` стало ограничено перечислением.

## Шаг 4. CRUD для главной сущности

Для временной базы были реализованы стандартные методы API.

### Эндпоинты для воинов

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/` | Проверка запуска приложения |
| `GET` | `/warriors_list` | Получение списка воинов |
| `GET` | `/warrior/{warrior_id}` | Получение одного воина |
| `POST` | `/warrior` | Создание воина |
| `PUT` | `/warrior/{warrior_id}` | Полное обновление воина |
| `DELETE` | `/warrior/delete/{warrior_id}` | Удаление воина |

Фрагменты маршрутов:

```python
@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.post("/warrior")
def warriors_create(
    warrior: Warrior,
) -> TypedDict("Response", {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}
```

## Шаг 5. API для вложенного объекта

По заданию практики нужно было сделать не только главную таблицу, но и API для вложенного объекта. Для этого была создана отдельная временная база `temp_professions`.

Пример:

```python
temp_professions = [
    {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    {
        "id": 2,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    },
]
```

### Эндпоинты для профессий

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/professions_list` | Получение списка профессий |
| `GET` | `/profession/{profession_id}` | Получение одной профессии |
| `POST` | `/profession` | Создание профессии |
| `PUT` | `/profession/{profession_id}` | Обновление профессии |
| `DELETE` | `/profession/delete/{profession_id}` | Удаление профессии |

Ключевой фрагмент:

```python
@app.post("/profession")
def professions_create(
    profession: Profession,
) -> TypedDict("Response", {"status": int, "data": Profession}):
    profession_to_append = profession.model_dump()
    temp_professions.append(profession_to_append)
    return {"status": 200, "data": profession}
```

## Итог практической работы

В результате была собрана первая учебная версия проекта на FastAPI:

- приложение запускается;
- работает корневой маршрут;
- есть временная база данных;
- главная сущность содержит вложенный объект и список объектов;
- реализован CRUD для главной сущности;
- реализован CRUD для вложенного объекта;
- данные описаны Pydantic-моделями;
- все маршруты видны в Swagger UI.

Эта практика стала базой для перехода к настоящей БД и ORM во второй практике.
