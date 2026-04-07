from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from models import Category, Task, TaskCreate, TaskUpdate, TaskWithRelations, TaskRead


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskRead])
def tasks_list(session: Session = Depends(get_session)) -> List[Task]:
    return session.exec(select(Task)).all()


@router.get("/{task_id}", response_model=TaskWithRelations)
def task_get(task_id: int, session: Session = Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskRead)
def task_create(task: TaskCreate, session: Session = Depends(get_session)) -> Task:
    if task.category_id is not None and not session.get(Category, task.category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=TaskRead)
def task_update(
    task_id: int, task: TaskUpdate, session: Session = Depends(get_session)
) -> Task:
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task.model_dump(exclude_unset=True)
    if "category_id" in update_data and update_data["category_id"] is not None:
        if not session.get(Category, update_data["category_id"]):
            raise HTTPException(status_code=404, detail="Category not found")
    for key, value in update_data.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/{task_id}")
def task_delete(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
