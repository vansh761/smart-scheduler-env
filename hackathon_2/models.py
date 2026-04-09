from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field
from typing import List, Optional

# -------- TASK MODEL -------- #
class Task(BaseModel):
    id: int = Field(..., description="Unique task ID", example=4)
    name: str = Field(..., description="Task name", example="Meeting")
    priority: int = Field(..., description="Task priority (1 = high, 3 = low)", example=1)
    start: Optional[int] = Field(None, description="Start time (hour of the day)", example=None)
    end: Optional[int] = Field(None, description="End time (hour of the day)", example=None)
    duration: int = Field(1, description="Task duration in hours", example=1)
    deadline: int = Field(12, description="Deadline hour", example=12)
    energy: str = Field("medium", description="Energy level required", example="medium")
    depends_on: Optional[int] = Field(None, description="Task ID this depends on", example=None)

# -------- ACTION MODEL -------- #
class Hackathon2Action(Action):
    task_id: int = Field(..., description="Task ID to act on", example=4)
    start_time: Optional[int] = Field(None, description="Start time for the task", example=9)
    end_time: Optional[int] = Field(None, description="End time for the task", example=10)
    duration: int = Field(1, description="Duration of the task", example=1)
    deadline: int = Field(12, description="Deadline of the task", example=12)
    energy: str = Field("medium", description="Energy level required", example="medium")
    depends_on: Optional[int] = Field(None, description="Task ID this depends on", example=None)

# -------- OBSERVATION MODEL -------- #
class Hackathon2Observation(Observation):
    message: str = Field(default="", description="Environment message", example="Environment reset. Schedule tasks.")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks", example=[
        {
            "id": 1,
            "name": "Study",
            "priority": 3,
            "start": None,
            "end": None,
            "duration": 2,
            "deadline": 10,
            "energy": "high",
            "depends_on": None
        },
        {
            "id": 2,
            "name": "Workout",
            "priority": 1,
            "start": None,
            "end": None,
            "duration": 1,
            "deadline": 8,
            "energy": "medium",
            "depends_on": None
        }
    ])
    conflicts: List[str] = Field(default_factory=list, description="Conflicts detected", example=[])
    scheduled: Optional[List[dict]] = Field(default_factory=list, description="Scheduled tasks with start/end", example=[
        {"task_id": 1, "start": 8, "end": 10, "priority": 3}
    ])
