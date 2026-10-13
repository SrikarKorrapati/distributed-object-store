from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime, timezone
from uuid import uuid4

Status = Literal["pending", "running", "completed", "failed"]
Priority = Literal["low", "medium", "high", "critical"]

PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: Priority = "medium"
    tags: list[str] = []
    agent: str = "default-agent"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be blank")
        if len(v) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return v


class Task(BaseModel):
    id: str
    title: str
    description: str
    status: Status
    priority: Priority
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    error: Optional[str] = None
    tags: list[str] = []
    agent: str


class TaskStats(BaseModel):
    total: int
    pending: int
    running: int
    completed: int
    failed: int


def make_task(body: TaskCreate) -> dict:
    return {
        "id": str(uuid4()),
        "title": body.title,
        "description": body.description.strip(),
        "status": "pending",
        "priority": body.priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "error": None,
        "tags": body.tags,
        "agent": body.agent,
    }
