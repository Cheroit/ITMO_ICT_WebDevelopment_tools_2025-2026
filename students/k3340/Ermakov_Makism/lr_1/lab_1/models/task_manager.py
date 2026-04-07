from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    done = "done"


class CategoryBase(SQLModel):
    name: str
    description: Optional[str] = ""


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class CategoryRead(CategoryBase):
    id: int


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TagBase(SQLModel):
    name: str
    color: Optional[str] = None


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_links: List["TaskTagLink"] = Relationship(
        back_populates="tag",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TagRead(TagBase):
    id: int


class TagUpdate(SQLModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.planned
    category_id: Optional[int] = None
    owner_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    category_id: Optional[int] = None
    owner_id: Optional[int] = None


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    category: Optional[Category] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    owner: Optional["User"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    time_entries: List["TimeEntry"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    tag_links: List["TaskTagLink"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    daily_plan_links: List["DailyPlanTaskLink"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TaskRead(TaskBase):
    id: int


class TaskShort(SQLModel):
    id: int
    title: str
    priority: TaskPriority
    status: TaskStatus
    deadline: Optional[datetime] = None


class TimeEntryBase(SQLModel):
    started_at: datetime
    minutes_spent: int
    notes: Optional[str] = ""
    task_id: int


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(SQLModel):
    started_at: Optional[datetime] = None
    minutes_spent: Optional[int] = None
    notes: Optional[str] = None
    task_id: Optional[int] = None


class TimeEntry(TimeEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    task: Optional[Task] = Relationship(
        back_populates="time_entries",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TimeEntryRead(TimeEntryBase):
    id: int


class TaskTagLinkBase(SQLModel):
    task_id: int
    tag_id: int
    importance: Optional[int] = None


class TaskTagLink(TaskTagLinkBase, table=True):
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    task: Optional[Task] = Relationship(
        back_populates="tag_links",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    tag: Optional[Tag] = Relationship(
        back_populates="task_links",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class TaskTagLinkCreate(TaskTagLinkBase):
    pass


class TaskTagLinkRead(TaskTagLinkBase):
    tag: Optional[TagRead] = None


class DailyPlanBase(SQLModel):
    plan_date: date
    title: str
    notes: Optional[str] = ""
    owner_id: Optional[int] = None


class DailyPlanCreate(DailyPlanBase):
    pass


class DailyPlanUpdate(SQLModel):
    plan_date: Optional[date] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    owner_id: Optional[int] = None


class DailyPlan(DailyPlanBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(
        back_populates="daily_plans",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    plan_tasks: List["DailyPlanTaskLink"] = Relationship(
        back_populates="daily_plan",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DailyPlanRead(DailyPlanBase):
    id: int


class DailyPlanTaskLinkBase(SQLModel):
    daily_plan_id: int
    task_id: int
    planned_minutes: Optional[int] = None


class DailyPlanTaskLink(DailyPlanTaskLinkBase, table=True):
    daily_plan_id: Optional[int] = Field(
        default=None, foreign_key="dailyplan.id", primary_key=True
    )
    task_id: Optional[int] = Field(
        default=None, foreign_key="task.id", primary_key=True
    )
    daily_plan: Optional[DailyPlan] = Relationship(
        back_populates="plan_tasks",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    task: Optional[Task] = Relationship(
        back_populates="daily_plan_links",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DailyPlanTaskLinkCreate(DailyPlanTaskLinkBase):
    pass


class DailyPlanTaskLinkRead(DailyPlanTaskLinkBase):
    task: Optional[TaskShort] = None


class TaskWithRelations(TaskRead):
    category: Optional[CategoryRead] = None
    time_entries: List[TimeEntryRead] = []
    tag_links: List[TaskTagLinkRead] = []


class DailyPlanWithTasks(DailyPlanRead):
    plan_tasks: List[DailyPlanTaskLinkRead] = []
