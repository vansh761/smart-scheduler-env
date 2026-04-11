from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# -------- TASK MODEL -------- #
class Task(BaseModel):
    id: int
    name: str
    priority: int
    start: Optional[int] = None
    end: Optional[int] = None

    # 🔥 REQUIRED FOR GRADER SYSTEM
    duration: int = 1
    deadline: int = 24
    energy: str = "medium"
    depends_on: Optional[int] = None

# -------- ACTION MODEL -------- #
class Hackathon2Action(Action):
    task_id: int = Field(..., description="Task ID to act on", example=4)
    name: Optional[str] = Field(None, description="Task name", example="Meeting")
    start_time: Optional[int] = Field(None, description="Start time for the task", example=9)
    priority: Optional[int] = Field(None, description="Task priority", example=1)
    energy: Optional[str] = Field("medium", description="Energy level required", example="medium")
    
    action_type: Literal["schedule", "move", "delete", "auto"] = Field(...,
        description="Choose action type: schedule / move / delete / auto"
    )
    
    
# -------- OBSERVATION MODEL -------- #
class Hackathon2Observation(Observation):
    message: str = Field(default="", description="Environment message", example="Environment reset. Schedule tasks.")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks", example=[
        {
            "id": 1,
            "name": "Study",
            "priority": 3,
            "start": None,
            "energy": "high"
        },
        {
            "id": 2,
            "name": "Workout",
            "priority": 1,
            "start": None,
            "energy": "medium"
        }
    ])
    conflicts: List[str] = Field(default_factory=list, description="Conflicts detected", example=[])
    scheduled: Optional[List[dict]] = Field(default_factory=list, description="Scheduled tasks with start", example=[
        {"task_id": 1, "start": 8, "priority": 3, "name": "Study"}
    ])
