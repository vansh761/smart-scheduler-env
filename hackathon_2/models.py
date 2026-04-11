from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class Task(BaseModel):
    id: int
    name: str
    priority: int
    duration: int = 1
    deadline: int = 10
    energy: str = "medium"
    score: float = Field(..., gt=0.0, lt=1.0)  # Keep this validation

class Hackathon2Action(Action):
    task_id: int = Field(..., description="Task ID to act on", example=4)
    name: Optional[str] = Field(None)
    start_time: Optional[int] = Field(None)
    priority: Optional[int] = Field(None)
    energy: Optional[str] = Field("medium")
    action_type: Literal["schedule", "move", "delete", "auto"]

class Hackathon2Observation(Observation):
    message: str = ""
    tasks: List[Task] = []
    conflicts: List[str] = []
    scheduled: Optional[List[dict]] = []
    meta: Optional[Dict] = None
