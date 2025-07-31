import enum

from pydantic import BaseModel


class Action(enum.Enum):
    WAIT = "wait"
    FAIL = "fail"
    PING = "ping"


class TaskMessage(BaseModel):
    task_id: str
    action: Action
    duration: float | None = None


class ResultMessage(BaseModel):
    task_id: str
    status: str
    result: str
    duration: float | None = None
