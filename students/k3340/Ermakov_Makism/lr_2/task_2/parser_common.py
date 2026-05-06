from __future__ import annotations

import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from os import environ
from pathlib import Path
from urllib.request import Request, urlopen

try:
    from sqlmodel import SQLModel, Session, create_engine, select
except ImportError as exc:
    raise SystemExit(
        "Для запуска парсеров установите зависимости: "
        "pip install -r students/k3340/Ermakov_Makism/lr_2/task_2/requirements.txt"
    ) from exc


LAB_1_PATH = Path(__file__).resolve().parents[2] / "lr_1" / "lab_1"
sys.path.insert(0, str(LAB_1_PATH))

from models.task_manager import Category, Task, TaskPriority, TaskStatus  # noqa: E402
from models.users import User  # noqa: F401, E402


def load_database_url() -> str:
    if "DB_ADMIN" in environ:
        return environ["DB_ADMIN"]

    env_path = LAB_1_PATH / ".env"

    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)

            if key.strip() == "DB_ADMIN":
                return value.strip().strip("'\"")

    raise RuntimeError("Не найден DB_ADMIN в окружении или в lr_1/lab_1/.env")


engine = create_engine(load_database_url(), echo=False)

URLS = [
    "https://docs.python.org/3/library/threading.html",
    "https://docs.python.org/3/library/multiprocessing.html",
    "https://docs.python.org/3/library/asyncio.html",
    "https://docs.python.org/3/library/html.parser.html",
    "https://docs.python.org/3/library/urllib.request.html",
    "https://docs.python.org/3/library/sqlite3.html",
]

TASK_CATEGORY_NAME = "Учебные материалы Python"
TASK_TITLE_PREFIX = "Изучить материал"
TASK_DESCRIPTION_PREFIX = "Учебный источник"
PARSER_WORKERS_COUNT = 3
REQUEST_TIMEOUT = 10


@dataclass
class ParsedPage:
    url: str
    title: str
    task_id: int | None
    action: str
    error: str | None = None


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._inside_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(" ".join(self._title_parts).split())


def split_urls(urls: list[str], parts: int) -> list[list[str]]:
    parts = max(1, min(parts, len(urls)))
    chunks = []

    for index in range(parts):
        start = index * len(urls) // parts
        end = (index + 1) * len(urls) // parts
        chunks.append(urls[start:end])

    return chunks


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ITMO-lr2-parser/1.0)"},
    )

    with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_title(html: str) -> str:
    parser = TitleParser()
    parser.feed(html)
    return parser.title


def build_task_title(page_title: str, url: str) -> str:
    title = page_title or f"страницу {url}"
    return f"{TASK_TITLE_PREFIX}: {title}"


def build_task_description(url: str) -> str:
    return f"{TASK_DESCRIPTION_PREFIX}: {url}"


def get_or_create_category(session: Session) -> Category:
    category = session.exec(
        select(Category).where(Category.name == TASK_CATEGORY_NAME)
    ).first()

    if category:
        return category

    category = Category(
        name=TASK_CATEGORY_NAME,
        description="Автоматически созданные задачи на изучение документации Python.",
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def save_title_to_db(url: str, title: str) -> tuple[int, str]:
    SQLModel.metadata.create_all(engine)
    task_title = build_task_title(title, url)
    source_description = build_task_description(url)

    with Session(engine) as session:
        category = get_or_create_category(session)
        existing_task = session.exec(
            select(Task).where(Task.description == source_description)
        ).first()

        if existing_task:
            existing_task.title = task_title
            existing_task.priority = TaskPriority.medium
            existing_task.status = TaskStatus.planned
            existing_task.category_id = category.id
            session.add(existing_task)
            session.commit()
            session.refresh(existing_task)
            return existing_task.id or 0, "updated"

        task = Task(
            title=task_title,
            description=source_description,
            priority=TaskPriority.medium,
            status=TaskStatus.planned,
            category_id=category.id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.id or 0, "created"


def parse_and_save_sync(url: str) -> ParsedPage:
    try:
        html = fetch_html(url)
        title = extract_title(html)
        task_id, action = save_title_to_db(url, title)
        result = ParsedPage(
            url=url,
            title=build_task_title(title, url),
            task_id=task_id,
            action=action,
        )
        print_result(result)
        return result
    except Exception as exc:
        result = ParsedPage(
            url=url,
            title="",
            task_id=None,
            action="failed",
            error=str(exc),
        )
        print_result(result)
        return result


def print_result(result: ParsedPage) -> None:
    if result.error:
        print(f"[failed] {result.url}: {result.error}")
        return

    print(f"[{result.action}] task_id={result.task_id} | {result.url} | {result.title}")
