from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=10)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    priority: Optional[int] = Field(None, ge=1, le=10)

class TaskOut(TaskBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class TaskLogOut(BaseModel):
    id: int
    task_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskDetail(TaskOut):
    logs: List[TaskLogOut] = []
