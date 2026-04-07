from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


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


class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class Skill(SkillDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors: List["Warrior"] = Relationship(
        back_populates="skills",
        link_model=SkillWarriorLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class SkillRead(SkillDefault):
    id: int


class ProfessionDefault(SQLModel):
    title: str
    description: str


class Profession(ProfessionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warriors_prof: List["Warrior"] = Relationship(
        back_populates="profession",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ProfessionRead(ProfessionDefault):
    id: int


class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = None


class WarriorUpdate(SQLModel):
    race: Optional[RaceType] = None
    name: Optional[str] = None
    level: Optional[int] = None
    profession_id: Optional[int] = None


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


class WarriorRead(WarriorDefault):
    id: int


class WarriorProfessions(WarriorRead):
    profession: Optional[ProfessionRead] = None


class WarriorWithRelations(WarriorProfessions):
    skills: List[SkillRead] = []
