from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from models import DailyPlan, DailyPlanCreate, DailyPlanRead, DailyPlanUpdate, DailyPlanWithTasks


router = APIRouter(prefix="/daily_plans", tags=["daily plans"])


@router.get("/", response_model=List[DailyPlanRead])
def daily_plans_list(session: Session = Depends(get_session)) -> List[DailyPlan]:
    return session.exec(select(DailyPlan)).all()


@router.get("/{daily_plan_id}", response_model=DailyPlanWithTasks)
def daily_plan_get(
    daily_plan_id: int, session: Session = Depends(get_session)
) -> DailyPlan:
    daily_plan = session.get(DailyPlan, daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    return daily_plan


@router.post("/", response_model=DailyPlanRead)
def daily_plan_create(
    daily_plan: DailyPlanCreate, session: Session = Depends(get_session)
) -> DailyPlan:
    db_daily_plan = DailyPlan.model_validate(daily_plan)
    session.add(db_daily_plan)
    session.commit()
    session.refresh(db_daily_plan)
    return db_daily_plan


@router.patch("/{daily_plan_id}", response_model=DailyPlanRead)
def daily_plan_update(
    daily_plan_id: int,
    daily_plan: DailyPlanUpdate,
    session: Session = Depends(get_session),
) -> DailyPlan:
    db_daily_plan = session.get(DailyPlan, daily_plan_id)
    if not db_daily_plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    for key, value in daily_plan.model_dump(exclude_unset=True).items():
        setattr(db_daily_plan, key, value)
    session.add(db_daily_plan)
    session.commit()
    session.refresh(db_daily_plan)
    return db_daily_plan


@router.delete("/{daily_plan_id}")
def daily_plan_delete(daily_plan_id: int, session: Session = Depends(get_session)):
    daily_plan = session.get(DailyPlan, daily_plan_id)
    if not daily_plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    session.delete(daily_plan)
    session.commit()
    return {"ok": True}
