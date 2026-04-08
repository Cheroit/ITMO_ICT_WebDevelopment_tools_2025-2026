# Практическая работа 1.2

## Тема работы

Во второй практике временная база данных была заменена на PostgreSQL, а модели переписаны на `SQLModel`. Основная задача этого этапа заключалась в переходе от списка словарей к полноценной ORM-модели с реальными таблицами, связями и запросами через сессии.

## Что требовалось по заданию

По итоговому заданию практики нужно было:

- подключить приложение к PostgreSQL;
- реализовать модели и API на SQLModel по своей теме;
- использовать связи `one-to-many` и `many-to-many`;
- сделать модели и API для many-to-many связи;
- реализовать вложенное отображение связанных объектов.

Практика выполнена в папке `lr_1/practice_1_2`.

## Шаг 1. Подключение PostgreSQL

Для работы с БД был создан файл `connection.py`, в котором настраивается соединение, создание таблиц и выдача сессий.

Ключевой код:

```python
from sqlmodel import SQLModel, Session, create_engine


db_url = "postgresql://postgres:1111@localhost/warriors_db"
engine = create_engine(db_url, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Здесь:

- `create_engine` создает подключение к PostgreSQL;
- `echo=True` выводит SQL-запросы в консоль;
- `init_db()` создает таблицы;
- `get_session()` используется в `Depends`.

## Шаг 2. Описание ORM-моделей

Во второй практике были реализованы следующие модели:

- `Profession`;
- `Skill`;
- `Warrior`;
- `SkillWarriorLink`.

Дополнительно были созданы модели для чтения и обновления:

- `ProfessionDefault`, `ProfessionRead`;
- `SkillDefault`, `SkillRead`;
- `WarriorDefault`, `WarriorRead`, `WarriorUpdate`;
- `WarriorProfessions`, `WarriorWithRelations`;
- `SkillWarriorLinkBase`.

### Основные связи

В проекте были реализованы две обязательные связи:

- `Profession -> Warrior` как `one-to-many`;
- `Warrior <-> Skill` как `many-to-many`.

Пример ассоциативной таблицы:

```python
class SkillWarriorLink(SkillWarriorLinkBase, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )
```

Пример главной таблицы:

```python
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
    profession: Optional[Profession] = Relationship(
        back_populates="warriors_prof",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    skills: List[Skill] = Relationship(
        back_populates="warriors",
        link_model=SkillWarriorLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
```

## Шаг 3. Автоматическое создание таблиц

В `main.py` был добавлен обработчик старта приложения:

```python
@app.on_event("startup")
def on_startup() -> None:
    init_db()
```

При запуске `uvicorn` таблицы создавались автоматически на основе `SQLModel.metadata`.

## Шаг 4. CRUD для главной сущности

После перехода на БД API перестал работать с временным списком и начал использовать `Session` и ORM-запросы.

Получение списка:

```python
@app.get("/warriors_list", response_model=List[WarriorRead])
def warriors_list(session: Session = Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()
```

Создание новой записи:

```python
@app.post("/warrior")
def warriors_create(
    warrior: WarriorDefault, session: Session = Depends(get_session)
) -> WarriorResponse:
    if warrior.profession_id is not None:
        _get_profession_or_404(session, warrior.profession_id)
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return {"status": 200, "data": db_warrior}
```

Частичное обновление:

```python
@app.patch("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warrior_update(
    warrior_id: int, warrior: WarriorUpdate, session: Session = Depends(get_session)
) -> Warrior:
    db_warrior = _get_warrior_or_404(session, warrior_id)
    warrior_data = warrior.model_dump(exclude_unset=True)
    ...
```

## Шаг 5. Вложенное отображение связанных объектов

Чтобы `GET /warrior/{warrior_id}` возвращал не только поля самого воина, но и связанные сущности, была введена отдельная модель ответа:

```python
class WarriorProfessions(WarriorRead):
    profession: Optional[ProfessionRead] = None


class WarriorWithRelations(WarriorProfessions):
    skills: List[SkillRead] = []
```

Использование в эндпоинте:

```python
@app.get("/warrior/{warrior_id}", response_model=WarriorWithRelations)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> Warrior:
    return _get_warrior_or_404(session, warrior_id)
```

В результате один запрос возвращал:

- данные воина;
- вложенную профессию;
- список связанных умений.

## Шаг 6. API для связанных сущностей

В практике были реализованы не только маршруты для главной сущности, но и отдельные API для профессий, умений и таблицы связи.

### Эндпоинты для воинов

| Метод | URL |
|---|---|
| `GET` | `/` |
| `GET` | `/warriors_list` |
| `GET` | `/warrior/{warrior_id}` |
| `POST` | `/warrior` |
| `PATCH` | `/warrior/{warrior_id}` |
| `DELETE` | `/warrior/delete/{warrior_id}` |

### Эндпоинты для профессий

| Метод | URL |
|---|---|
| `GET` | `/professions_list` |
| `GET` | `/profession/{profession_id}` |
| `POST` | `/profession` |
| `PATCH` | `/profession/{profession_id}` |
| `DELETE` | `/profession/delete/{profession_id}` |

### Эндпоинты для умений

| Метод | URL |
|---|---|
| `GET` | `/skills_list` |
| `GET` | `/skill/{skill_id}` |
| `POST` | `/skill` |
| `PATCH` | `/skill/{skill_id}` |
| `DELETE` | `/skill/delete/{skill_id}` |

### Эндпоинты для many-to-many связи

| Метод | URL |
|---|---|
| `GET` | `/skill_links` |
| `GET` | `/skill_link/{warrior_id}/{skill_id}` |
| `POST` | `/skill_link` |
| `DELETE` | `/skill_link/{warrior_id}/{skill_id}` |

Пример создания связи:

```python
@app.post("/skill_link")
def skill_link_create(
    link: SkillWarriorLinkBase, session: Session = Depends(get_session)
) -> LinkResponse:
    _get_warrior_or_404(session, link.warrior_id)
    _get_skill_or_404(session, link.skill_id)
    ...
```

## Итог практической работы

Во второй практике проект перешел от учебной временной структуры к полноценному серверному приложению с PostgreSQL:

- подключена настоящая БД;
- реализованы таблицы на SQLModel;
- использованы `one-to-many` и `many-to-many` связи;
- сделаны CRUD-методы через ORM;
- реализовано вложенное отображение связанных объектов;
- добавлено API для связанной many-to-many сущности.

Этот этап стал прямой основой для третьей практики, где к проекту были добавлены миграции, `.env` и более аккуратная структура.
