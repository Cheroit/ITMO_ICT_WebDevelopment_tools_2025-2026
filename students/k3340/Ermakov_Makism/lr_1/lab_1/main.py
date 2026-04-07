from api.auth import router as auth_router
from fastapi import FastAPI

from api.categories import router as categories_router
from api.daily_plans import router as daily_plans_router
from api.links import router as links_router
from api.tags import router as tags_router
from api.tasks import router as tasks_router
from api.time_entries import router as time_entries_router
from api.users import router as users_router
from db.connection import init_db


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
