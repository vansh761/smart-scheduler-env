from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field
from typing import List, Optional


# -------- TASK MODEL -------- #
class Task(BaseModel):
    id: int = Field(..., description="Unique task ID")
    name: str = Field(..., description="Task name")
    priority: int = Field(..., description="Task priority (1 = high)")
    start: Optional[int] = Field(None, description="Start time")
    end: Optional[int] = Field(None, description="End time")
    duration: int = 1
    deadline: int = 10
    energy: str = "medium"
    depends_on: Optional[int] = None


# -------- ACTION MODEL -------- #
class Hackathon2Action(Action):
    action_type: str = Field(..., description="Type: schedule/move/delete/finish")
    task_id: Optional[int] = Field(None, description="Task ID")
    start: Optional[int] = Field(None, description="Start time")
    end: Optional[int] = Field(None, description="End time")
    duration: int = 1
    deadline: int = 24
    energy: str = "medium"
    depends_on: Optional[int] = None

# -------- OBSERVATION MODEL -------- #
class Hackathon2Observation(Observation):
    message: str = Field(default="", description="Environment message")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks")
    conflicts: List[str] = Field(default_factory=list, description="Conflicts detected")