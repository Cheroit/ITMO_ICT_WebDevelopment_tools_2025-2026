from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from models import Tag, TagBase, TagRead, TagUpdate


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagRead])
def tags_list(session: Session = Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@router.get("/{tag_id}", response_model=TagRead)
def tag_get(tag_id: int, session: Session = Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/", response_model=TagRead)
def tag_create(tag: TagBase, session: Session = Depends(get_session)) -> Tag:
    db_tag = Tag.model_validate(tag)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.patch("/{tag_id}", response_model=TagRead)
def tag_update(
    tag_id: int, tag: TagUpdate, session: Session = Depends(get_session)
) -> Tag:
    db_tag = session.get(Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    for key, value in tag.model_dump(exclude_unset=True).items():
        setattr(db_tag, key, value)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}")
def tag_delete(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    return {"ok": True}
