# Практическая работа 1.3

## Тема работы

Третья практика была посвящена организационным улучшениям проекта:

- миграциям через Alembic;
- хранению конфигурации в `.env`;
- настройке `.gitignore`;
- улучшению структуры проекта.

Практика выполнена в папке `lr_1/practice_1_3`.

## Что требовалось по заданию

По методическим указаниям нужно было:

- подключить Alembic;
- создать папку `migrations`;
- настроить `alembic.ini` и `env.py`;
- реализовать передачу URL БД из `.env` в Alembic;
- добавить поле `level` к ассоциативной сущности `SkillWarriorLink`;
- сгенерировать и применить миграцию;
- оформить `.gitignore`.

## Шаг 1. Обновление структуры проекта

После выполнения второй практики проект был расширен. В папке `practice_1_3` появились:

- `main.py`;
- `connection.py`;
- `models.py`;
- `.env`;
- `.gitignore`;
- `alembic.ini`;
- папка `migrations/`.

Это соответствует требованию по более аккуратной файловой структуре.

## Шаг 2. Хранение URL базы в `.env`

Строка подключения была вынесена из исходного кода в отдельный файл `.env`.

Пример:

```env
DB_ADMIN=postgresql://postgres:<password>@localhost/warriors_db
```

В `connection.py` подключение выглядит так:

```python
import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine


load_dotenv()
db_url = os.getenv("DB_ADMIN")
engine = create_engine(db_url, echo=True)
```

Такой подход лучше обычной строки в коде, потому что:

- чувствительные данные не попадают в репозиторий;
- один и тот же проект легче запускать в разных средах;
- строку подключения можно менять без правки исходников.

## Шаг 3. Настройка `.gitignore`

Чтобы не коммитить служебные и чувствительные файлы, был добавлен `.gitignore`.

Пример содержимого:

```text
*.env
__pycache__/
.idea/
.venv/
*.pyc
site
```

В результате Git перестает отслеживать:

- `.env`;
- временные файлы Python;
- папки IDE;
- виртуальное окружение;
- локальную сборку документации.

## Шаг 4. Инициализация Alembic

Для миграций использовалась стандартная команда:

```bash
alembic init migrations
```

После этого в проекте появились:

```text
migrations/
├─ versions/
├─ env.py
├─ README
├─ script.py.mako
alembic.ini
```

## Шаг 5. Настройка `env.py` для SQLModel и `.env`

Чтобы Alembic видел модели проекта и мог брать строку подключения из переменных окружения, был настроен файл `migrations/env.py`.

Ключевой фрагмент:

```python
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from models import *  # noqa: F401,F403

load_dotenv()

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DB_ADMIN", ""))
target_metadata = SQLModel.metadata
```

Здесь выполнены два важных условия из задания:

- Alembic видит `SQLModel.metadata`;
- URL базы передается через `.env`.

## Шаг 6. Изменение ассоциативной сущности

В рамках практики нужно было добавить поле, характеризующее связь между воином и умением.

В текущей реализации это поле описано в базовой модели связи и затем наследуется таблицей:

```python
class SkillWarriorLinkBase(SQLModel):
    skill_id: int
    warrior_id: int
    level: Optional[int] = None


class SkillWarriorLink(SkillWarriorLinkBase, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
    )
```

По смыслу это полностью соответствует требованию методички: связь получила дополнительное поле `level`.

## Шаг 7. Создание и применение миграции

После изменения модели была сгенерирована миграция:

```bash
alembic revision --autogenerate -m "skill added"
alembic upgrade head
```

Сгенерированная миграция добавляет столбец `level` в таблицу `skillwarriorlink`:

```python
def upgrade() -> None:
    op.add_column("skillwarriorlink", sa.Column("level", sa.Integer(), nullable=True))
```

Это и есть основной результат третьей практики: изменение модели было внесено в базу не вручную, а через систему миграций.

## Итог практической работы

После завершения практики `1.3` проект получил все улучшения, которые требовались перед началом итоговой лабораторной работы:

- конфигурацию подключения через `.env`;
- рабочий `.gitignore`;
- структуру `migrations/`;
- Alembic;
- передачу URL БД из `.env` в `env.py`;
- миграцию для изменения ассоциативной сущности.

Этот этап завершил подготовку проекта к итоговой лабораторной работе.
