# Лабораторная работа 1

## Тема и цель

Тема лабораторной работы: `Разработка серверного приложения FastAPI по теме тайм-менеджера`.

Цель работы состояла в том, чтобы собрать полноценное серверное приложение, которое объединяет все знания из практик:

- FastAPI и базовые маршруты;
- модели и типизацию;
- PostgreSQL и SQLModel;
- связи `one-to-many` и `many-to-many`;
- Alembic;
- `.env` и `.gitignore`;
- структурирование проекта по папкам;
- пользовательский функционал, JWT и смену пароля.

## Постановка задачи

По заданию нужно было разработать программу-тайм-менеджер, позволяющую:

- создавать задачи;
- задавать описание, приоритет и дедлайн;
- отслеживать затраченное время;
- формировать ежедневное расписание;
- использовать связи между сущностями;
- при расширении до 15 баллов реализовать пользователей и JWT-аутентификацию.

## Структура итогового проекта

Итоговое приложение находится в папке `lr_1/lab_1`.

Структура проекта:

```text
lab_1/
├─ api/
│  ├─ auth.py
│  ├─ categories.py
│  ├─ daily_plans.py
│  ├─ links.py
│  ├─ tags.py
│  ├─ tasks.py
│  ├─ time_entries.py
│  └─ users.py
├─ core/
│  └─ security.py
├─ db/
│  └─ connection.py
├─ migrations/
│  ├─ env.py
│  └─ versions/
├─ models/
│  ├─ task_manager.py
│  └─ users.py
├─ .env
├─ .gitignore
├─ alembic.ini
└─ main.py
```

Такое разбиение помогает разделить проект на независимые части:

- `api/` — маршруты;
- `models/` — модели предметной области;
- `db/` — подключение к базе;
- `core/` — безопасность и JWT;
- `migrations/` — Alembic;
- `main.py` — точка входа.

## Подключение к базе данных

В отчете обязательно должен быть приведен код соединения с БД, поэтому ниже показан финальный вариант файла `db/connection.py`.

```python
import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine


load_dotenv()
db_url = os.getenv("DB_ADMIN")
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Подключение использует переменную окружения `DB_ADMIN`, поэтому данные доступа к PostgreSQL не хранятся в коде.

## Точка входа приложения

Файл `main.py` собирает приложение и подключает все роутеры:

```python
app = FastAPI(title="Time Manager API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def hello() -> str:
    return "Time Manager API is ready"


app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(tasks_router)
app.include_router(time_entries_router)
app.include_router(daily_plans_router)
app.include_router(links_router)
app.include_router(auth_router)
app.include_router(users_router)
```

## Модель данных

По требованиям лабораторной работы модель данных должна включать:

- не менее пяти таблиц;
- связи `one-to-many` и `many-to-many`;
- ассоциативную сущность с дополнительным полем.

Эти требования выполнены.

### Таблицы проекта

В приложении используются следующие таблицы:

| Таблица | Назначение |
|---|---|
| `category` | Категории задач |
| `tag` | Теги задач |
| `task` | Основная таблица задач |
| `timeentry` | Фактически затраченное время |
| `dailyplan` | Ежедневные планы |
| `tasktaglink` | Связь задач и тегов |
| `dailyplantasklink` | Связь планов и задач |
| `user` | Пользователи приложения |

### Главная сущность

Главной таблицей является `Task`, потому что именно вокруг нее строится предметная область тайм-менеджера.

```python
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.planned
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
```

Эта модель хранит:

- название задачи;
- описание;
- дедлайн;
- приоритет;
- статус;
- связь с категорией;
- связь с владельцем.

### Связи `one-to-many`

В проекте реализованы следующие связи `one-to-many`:

| Связь | Описание |
|---|---|
| `Category -> Task` | одна категория содержит много задач |
| `Task -> TimeEntry` | одна задача имеет много записей времени |
| `User -> Task` | один пользователь может создать много задач |
| `User -> DailyPlan` | один пользователь может иметь много ежедневных планов |

Пример связи категории и задач:

```python
class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
```

### Связи `many-to-many`

В проекте реализованы две связи `many-to-many`:

| Связь | Промежуточная таблица |
|---|---|
| `Task <-> Tag` | `TaskTagLink` |
| `DailyPlan <-> Task` | `DailyPlanTaskLink` |

### Ассоциативные сущности с дополнительным полем

Требование лабораторной о дополнительном поле связи выполнено дважды.

Связь задачи и тега:

```python
class TaskTagLinkBase(SQLModel):
    task_id: int
    tag_id: int
    importance: Optional[int] = None
```

Связь ежедневного плана и задачи:

```python
class DailyPlanTaskLinkBase(SQLModel):
    daily_plan_id: int
    task_id: int
    planned_minutes: Optional[int] = None
```

Поля характеризуют саму связь:

- `importance` показывает, насколько важен тег для конкретной задачи;
- `planned_minutes` показывает, сколько минут планируется потратить на задачу в рамках выбранного плана.

## Реализованные модели

По условию отчета необходимо перечислить все реализованные модели. Ниже приведена итоговая структура моделей.

### Модели предметной области

В файле `models/task_manager.py` реализованы:

- перечисления `TaskPriority` и `TaskStatus`;
- `CategoryBase`, `Category`, `CategoryRead`, `CategoryUpdate`;
- `TagBase`, `Tag`, `TagRead`, `TagUpdate`;
- `TaskBase`, `TaskCreate`, `TaskUpdate`, `Task`, `TaskRead`, `TaskShort`;
- `TimeEntryBase`, `TimeEntryCreate`, `TimeEntryUpdate`, `TimeEntry`, `TimeEntryRead`;
- `TaskTagLinkBase`, `TaskTagLink`, `TaskTagLinkCreate`, `TaskTagLinkRead`;
- `DailyPlanBase`, `DailyPlanCreate`, `DailyPlanUpdate`, `DailyPlan`, `DailyPlanRead`;
- `DailyPlanTaskLinkBase`, `DailyPlanTaskLink`, `DailyPlanTaskLinkCreate`, `DailyPlanTaskLinkRead`;
- модели вложенного вывода `TaskWithRelations` и `DailyPlanWithTasks`.

Пример вложенной модели ответа:

```python
class TaskWithRelations(TaskRead):
    category: Optional[CategoryRead] = None
    time_entries: List[TimeEntryRead] = []
    tag_links: List[TaskTagLinkRead] = []
```

Она используется для возврата задачи вместе со связанными объектами.

### Пользовательские модели

В файле `models/users.py` реализованы:

- `UserBase`;
- `UserCreate`;
- `UserLogin`;
- `UserPasswordChange`;
- `User`;
- `UserRead`;
- `TokenResponse`.

Ключевой фрагмент:

```python
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    daily_plans: List["DailyPlan"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
```

## Реализованные эндпоинты

По условиям отчета нужно показать все реализованные API. Ниже приведен полный список маршрутов финальной версии приложения.

### Базовый маршрут

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/` | Проверка запуска API |

### Категории

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/categories/` | Список категорий |
| `GET` | `/categories/{category_id}` | Одна категория |
| `POST` | `/categories/` | Создание категории |
| `PATCH` | `/categories/{category_id}` | Обновление категории |
| `DELETE` | `/categories/{category_id}` | Удаление категории |

### Теги

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/tags/` | Список тегов |
| `GET` | `/tags/{tag_id}` | Один тег |
| `POST` | `/tags/` | Создание тега |
| `PATCH` | `/tags/{tag_id}` | Обновление тега |
| `DELETE` | `/tags/{tag_id}` | Удаление тега |

### Задачи

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/tasks/` | Список задач |
| `GET` | `/tasks/{task_id}` | Одна задача с вложенными связями |
| `POST` | `/tasks/` | Создание задачи |
| `PATCH` | `/tasks/{task_id}` | Обновление задачи |
| `DELETE` | `/tasks/{task_id}` | Удаление задачи |

Эндпоинт `GET /tasks/{task_id}` возвращает модель `TaskWithRelations`, то есть:

- саму задачу;
- категорию;
- записи затраченного времени;
- связанные теги через ассоциативную сущность.

### Записи времени

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/time_entries/` | Список записей времени |
| `GET` | `/time_entries/{time_entry_id}` | Одна запись времени |
| `POST` | `/time_entries/` | Создание записи времени |
| `PATCH` | `/time_entries/{time_entry_id}` | Обновление записи времени |
| `DELETE` | `/time_entries/{time_entry_id}` | Удаление записи времени |

### Ежедневные планы

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/daily_plans/` | Список планов |
| `GET` | `/daily_plans/{daily_plan_id}` | Один план с вложенными задачами |
| `POST` | `/daily_plans/` | Создание плана |
| `PATCH` | `/daily_plans/{daily_plan_id}` | Обновление плана |
| `DELETE` | `/daily_plans/{daily_plan_id}` | Удаление плана |

Эндпоинт `GET /daily_plans/{daily_plan_id}` возвращает `DailyPlanWithTasks`, то есть план вместе с задачами из промежуточной таблицы.

### Связи задача-тег

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/task_tags` | Список связей задача-тег |
| `POST` | `/task_tags` | Создание связи задача-тег |
| `DELETE` | `/task_tags/{task_id}/{tag_id}` | Удаление связи задача-тег |

### Связи план-задача

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/daily_plan_tasks` | Список связей план-задача |
| `POST` | `/daily_plan_tasks` | Создание связи план-задача |
| `DELETE` | `/daily_plan_tasks/{daily_plan_id}/{task_id}` | Удаление связи план-задача |

### Авторизация и регистрация

| Метод | URL | Назначение |
|---|---|---|
| `POST` | `/auth/register` | Регистрация пользователя |
| `POST` | `/auth/login` | Вход и получение JWT |

### Пользовательские методы

| Метод | URL | Назначение |
|---|---|---|
| `GET` | `/users/` | Список пользователей |
| `GET` | `/users/me` | Информация о текущем пользователе |
| `POST` | `/users/change-password` | Смена пароля |

## CRUD и вложенные ответы

Требование лабораторной о CRUD и вложенных моделях также выполнено.

### Пример вложенного `GET` для задачи

```python
@router.get("/{task_id}", response_model=TaskWithRelations)
def task_get(task_id: int, session: Session = Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Пример вложенного `GET` для ежедневного плана

```python
@router.get("/{daily_plan_id}", response_model=DailyPlanWithTasks)
def daily_plan_get(
    daily_plan_id: int, session: Session = Depends(get_session)
) -> DailyPlan:
    daily_plan = session.get(DailyPlan, daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    return daily_plan
```

## Миграции Alembic

Для лабораторной работы была настроена система миграций Alembic. В проекте используются:

- `alembic.ini`;
- `migrations/env.py`;
- папка `migrations/versions/`.

`env.py` работает с `.env` и `SQLModel.metadata`, поэтому миграции видят все модели проекта.

Команды, использовавшиеся в работе:

```bash
alembic revision --autogenerate -m "init time manager"
alembic upgrade head
alembic revision --autogenerate -m "add users auth"
alembic upgrade head
```

## Реализация задания на 15 баллов

Дополнительно в проекте реализован пользовательский функционал.

### Регистрация

```python
@router.post("/register", response_model=UserRead)
def register_user(
    user: UserCreate, session: Session = Depends(get_session)
) -> User:
    existing_user = session.exec(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    ...
```

### Логин и получение JWT

```python
@router.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin, session: Session = Depends(get_session)) -> TokenResponse:
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(db_user.id, db_user.username)
    return TokenResponse(access_token=token)
```

### Хэширование паролей

По условию задания хэширование было сделано вручную, без сторонних библиотек для готовой авторизации.

```python
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}${password_hash.hex()}"
```

### JWT-аутентификация

JWT также реализован вручную в `core/security.py` через:

- `base64`;
- `json`;
- `hmac`;
- `hashlib`.

Пример создания токена:

```python
def create_access_token(user_id: int, username: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": ...
    }
```

### Получение текущего пользователя

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_access_token(credentials.credentials)
    user_id = int(payload.get("sub"))
    user = session.get(User, user_id)
```

Через этот механизм защищены эндпоинты:

- `/users/`;
- `/users/me`;
- `/users/change-password`.

## Проверка результата

В ходе выполнения лабораторной были проверены:

- запуск FastAPI-приложения;
- создание и чтение категорий;
- создание и чтение тегов;
- создание задач и получение вложенных данных;
- создание записей времени;
- создание ежедневных планов;
- создание many-to-many связей;
- регистрация пользователя;
- логин и получение JWT;
- доступ к защищенным маршрутам;
- смена пароля и повторная авторизация.

## Итог

В результате была реализована полноценная учебная серверная система на FastAPI, которая соответствует требованиям лабораторной работы:

- используется PostgreSQL;
- данные описаны через SQLModel;
- реализованы CRUD-методы;
- настроен Alembic;
- используется `.env`;
- проект разделен по папкам;
- есть вложенные `GET`-запросы;
- выполнены требования из практик `1.1`, `1.2` и `1.3`;
- дополнительно реализованы регистрация, JWT, аутентификация и смена пароля.

Итоговый проект показывает полный путь от базового FastAPI-приложения до структурированного серверного API с базой данных, миграциями и пользовательской авторизацией.
