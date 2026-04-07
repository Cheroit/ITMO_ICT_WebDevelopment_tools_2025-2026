from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    email: str = Field(index=True, sa_column_kwargs={"unique": True})


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserPasswordChange(SQLModel):
    old_password: str
    new_password: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    daily_plans: List["DailyPlan"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class UserRead(UserBase):
    id: int
    created_at: datetime


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
