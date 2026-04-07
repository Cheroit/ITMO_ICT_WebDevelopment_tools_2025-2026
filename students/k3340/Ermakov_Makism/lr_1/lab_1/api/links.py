from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from models import (
    DailyPlan,
    DailyPlanTaskLink,
    DailyPlanTaskLinkCreate,
    DailyPlanTaskLinkRead,
    Tag,
    Task,
    TaskTagLink,
    TaskTagLinkCreate,
    TaskTagLinkRead,
)


router = APIRouter(tags=["links"])


@router.get("/task_tags", response_model=List[TaskTagLinkRead])
def task_tags_list(session: Session = Depends(get_session)) -> List[TaskTagLink]:
    return session.exec(select(TaskTagLink)).all()


@router.post("/task_tags", response_model=TaskTagLinkRead)
def task_tag_create(
    task_tag: TaskTagLinkCreate, session: Session = Depends(get_session)
) -> TaskTagLink:
    if not session.get(Task, task_tag.task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    if not session.get(Tag, task_tag.tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    existing_link = session.exec(
        select(TaskTagLink).where(
            TaskTagLink.task_id == task_tag.task_id,
            TaskTagLink.tag_id == task_tag.tag_id,
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Task tag link already exists")
    db_task_tag = TaskTagLink.model_validate(task_tag)
    session.add(db_task_tag)
    session.commit()
    session.refresh(db_task_tag)
    return db_task_tag


@router.delete("/task_tags/{task_id}/{tag_id}")
def task_tag_delete(task_id: int, tag_id: int, session: Session = Depends(get_session)):
    task_tag = session.exec(
        select(TaskTagLink).where(
            TaskTagLink.task_id == task_id,
            TaskTagLink.tag_id == tag_id,
        )
    ).first()
    if not task_tag:
        raise HTTPException(status_code=404, detail="Task tag link not found")
    session.delete(task_tag)
    session.commit()
    return {"ok": True}


@router.get("/daily_plan_tasks", response_model=List[DailyPlanTaskLinkRead])
def daily_plan_tasks_list(
    session: Session = Depends(get_session),
) -> List[DailyPlanTaskLink]:
    return session.exec(select(DailyPlanTaskLink)).all()


@router.post("/daily_plan_tasks", response_model=DailyPlanTaskLinkRead)
def daily_plan_task_create(
    daily_plan_task: DailyPlanTaskLinkCreate, session: Session = Depends(get_session)
) -> DailyPlanTaskLink:
    if not session.get(DailyPlan, daily_plan_task.daily_plan_id):
        raise HTTPException(status_code=404, detail="Daily plan not found")
    if not session.get(Task, daily_plan_task.task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    existing_link = session.exec(
        select(DailyPlanTaskLink).where(
            DailyPlanTaskLink.daily_plan_id == daily_plan_task.daily_plan_id,
            DailyPlanTaskLink.task_id == daily_plan_task.task_id,
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Daily plan task link already exists")
    db_daily_plan_task = DailyPlanTaskLink.model_validate(daily_plan_task)
    session.add(db_daily_plan_task)
    session.commit()
    session.refresh(db_daily_plan_task)
    return db_daily_plan_task


@router.delete("/daily_plan_tasks/{daily_plan_id}/{task_id}")
def daily_plan_task_delete(
    daily_plan_id: int, task_id: int, session: Session = Depends(get_session)
):
    daily_plan_task = session.exec(
        select(DailyPlanTaskLink).where(
            DailyPlanTaskLink.daily_plan_id == daily_plan_id,
            DailyPlanTaskLink.task_id == task_id,
        )
    ).first()
    if not daily_plan_task:
        raise HTTPException(status_code=404, detail="Daily plan task link not found")
    session.delete(daily_plan_task)
    session.commit()
    return {"ok": True}
