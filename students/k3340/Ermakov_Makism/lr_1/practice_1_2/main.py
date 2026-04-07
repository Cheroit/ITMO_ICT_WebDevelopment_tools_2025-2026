from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from connection import get_session, init_db
from models import (
    Profession,
    ProfessionDefault,
    ProfessionRead,
    Skill,
    SkillDefault,
    SkillRead,
    SkillWarriorLink,
    SkillWarriorLinkBase,
    Warrior,
    WarriorDefault,
    WarriorProfessions,
    WarriorRead,
    WarriorUpdate,
    WarriorWithRelations,
)


class WarriorResponse(TypedDict):
    status: int
    data: WarriorRead


class ProfessionResponse(TypedDict):
    status: int
    data: ProfessionRead


class SkillResponse(TypedDict):
    status: int
    data: SkillRead


class LinkResponse(TypedDict):
    status: int
    data: SkillWarriorLinkBase


app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _get_profession_or_404(session: Session, profession_id: int) -> Profession:
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


def _get_skill_or_404(session: Session, skill_id: int) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


def _get_warrior_or_404(session: Session, warrior_id: int) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.get("/")
def hello() -> str:
    return "Practice 1.2 is ready"


@app.get("/warriors_list", response_model=List[WarriorRead])
def warriors_list(session: Session = Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorWithRelations)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> Warrior:
    return _get_warrior_or_404(session, warrior_id)


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


@app.patch("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warrior_update(
    warrior_id: int, warrior: WarriorUpdate, session: Session = Depends(get_session)
) -> Warrior:
    db_warrior = _get_warrior_or_404(session, warrior_id)
    warrior_data = warrior.model_dump(exclude_unset=True)

    if "profession_id" in warrior_data and warrior_data["profession_id"] is not None:
        _get_profession_or_404(session, warrior_data["profession_id"])

    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)):
    warrior = _get_warrior_or_404(session, warrior_id)
    links = session.exec(
        select(SkillWarriorLink).where(SkillWarriorLink.warrior_id == warrior_id)
    ).all()
    for link in links:
        session.delete(link)
    session.delete(warrior)
    session.commit()
    return {"ok": True}


@app.get("/professions_list", response_model=List[ProfessionRead])
def professions_list(session: Session = Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}", response_model=ProfessionRead)
def profession_get(
    profession_id: int, session: Session = Depends(get_session)
) -> Profession:
    return _get_profession_or_404(session, profession_id)


@app.post("/profession")
def profession_create(
    profession: ProfessionDefault, session: Session = Depends(get_session)
) -> ProfessionResponse:
    db_profession = Profession.model_validate(profession)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return {"status": 200, "data": db_profession}


@app.patch("/profession/{profession_id}", response_model=ProfessionRead)
def profession_update(
    profession_id: int,
    profession: ProfessionDefault,
    session: Session = Depends(get_session),
) -> Profession:
    db_profession = _get_profession_or_404(session, profession_id)
    profession_data = profession.model_dump(exclude_unset=True)
    for key, value in profession_data.items():
        setattr(db_profession, key, value)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.delete("/profession/delete/{profession_id}")
def profession_delete(
    profession_id: int, session: Session = Depends(get_session)
):
    profession = _get_profession_or_404(session, profession_id)
    warriors = session.exec(
        select(Warrior).where(Warrior.profession_id == profession_id)
    ).all()
    for warrior in warriors:
        warrior.profession_id = None
        session.add(warrior)
    session.delete(profession)
    session.commit()
    return {"ok": True}


@app.get("/skills_list", response_model=List[SkillRead])
def skills_list(session: Session = Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}", response_model=SkillRead)
def skill_get(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    return _get_skill_or_404(session, skill_id)


@app.post("/skill")
def skill_create(
    skill: SkillDefault, session: Session = Depends(get_session)
) -> SkillResponse:
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return {"status": 200, "data": db_skill}


@app.patch("/skill/{skill_id}", response_model=SkillRead)
def skill_update(
    skill_id: int, skill: SkillDefault, session: Session = Depends(get_session)
) -> Skill:
    db_skill = _get_skill_or_404(session, skill_id)
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int, session: Session = Depends(get_session)):
    skill = _get_skill_or_404(session, skill_id)
    links = session.exec(
        select(SkillWarriorLink).where(SkillWarriorLink.skill_id == skill_id)
    ).all()
    for link in links:
        session.delete(link)
    session.delete(skill)
    session.commit()
    return {"ok": True}


@app.get("/skill_links", response_model=List[SkillWarriorLinkBase])
def skill_links_list(
    session: Session = Depends(get_session),
) -> List[SkillWarriorLink]:
    return session.exec(select(SkillWarriorLink)).all()


@app.get("/skill_link/{warrior_id}/{skill_id}", response_model=SkillWarriorLinkBase)
def skill_link_get(
    warrior_id: int, skill_id: int, session: Session = Depends(get_session)
) -> SkillWarriorLink:
    link = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == warrior_id,
            SkillWarriorLink.skill_id == skill_id,
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Skill link not found")
    return link


@app.post("/skill_link")
def skill_link_create(
    link: SkillWarriorLinkBase, session: Session = Depends(get_session)
) -> LinkResponse:
    _get_warrior_or_404(session, link.warrior_id)
    _get_skill_or_404(session, link.skill_id)

    existing_link = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == link.warrior_id,
            SkillWarriorLink.skill_id == link.skill_id,
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Skill link already exists")

    db_link = SkillWarriorLink.model_validate(link)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return {"status": 200, "data": db_link}


@app.delete("/skill_link/{warrior_id}/{skill_id}")
def skill_link_delete(
    warrior_id: int, skill_id: int, session: Session = Depends(get_session)
):
    link = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == warrior_id,
            SkillWarriorLink.skill_id == skill_id,
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Skill link not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
