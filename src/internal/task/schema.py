from typing import Any

from pydantic import BaseModel, Field


class TaskResult(BaseModel):
    task_id: str
    status: str
    result: Any


class CreateTask(BaseModel):
    task_id: str = Field(examples=["78bafacd-c769-4c6f-a07e-870f595f9373"])
