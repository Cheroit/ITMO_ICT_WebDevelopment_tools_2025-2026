from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from models import Task, TimeEntry, TimeEntryCreate, TimeEntryRead, TimeEntryUpdate


router = APIRouter(prefix="/time_entries", tags=["time entries"])


@router.get("/", response_model=List[TimeEntryRead])
def time_entries_list(session: Session = Depends(get_session)) -> List[TimeEntry]:
    return session.exec(select(TimeEntry)).all()


@router.get("/{time_entry_id}", response_model=TimeEntryRead)
def time_entry_get(
    time_entry_id: int, session: Session = Depends(get_session)
) -> TimeEntry:
    time_entry = session.get(TimeEntry, time_entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return time_entry


@router.post("/", response_model=TimeEntryRead)
def time_entry_create(
    time_entry: TimeEntryCreate, session: Session = Depends(get_session)
) -> TimeEntry:
    if not session.get(Task, time_entry.task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    db_time_entry = TimeEntry.model_validate(time_entry)
    session.add(db_time_entry)
    session.commit()
    session.refresh(db_time_entry)
    return db_time_entry


@router.patch("/{time_entry_id}", response_model=TimeEntryRead)
def time_entry_update(
    time_entry_id: int,
    time_entry: TimeEntryUpdate,
    session: Session = Depends(get_session),
) -> TimeEntry:
    db_time_entry = session.get(TimeEntry, time_entry_id)
    if not db_time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    update_data = time_entry.model_dump(exclude_unset=True)
    if "task_id" in update_data and not session.get(Task, update_data["task_id"]):
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in update_data.items():
        setattr(db_time_entry, key, value)
    session.add(db_time_entry)
    session.commit()
    session.refresh(db_time_entry)
    return db_time_entry


@router.delete("/{time_entry_id}")
def time_entry_delete(time_entry_id: int, session: Session = Depends(get_session)):
    time_entry = session.get(TimeEntry, time_entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    session.delete(time_entry)
    session.commit()
    return {"ok": True}
