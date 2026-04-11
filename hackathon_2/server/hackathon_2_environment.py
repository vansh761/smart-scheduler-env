from uuid import uuid4
from typing import List
import random  

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import Hackathon2Action, Hackathon2Observation, Task
except ImportError:
    from models import Hackathon2Action, Hackathon2Observation, Task


class Hackathon2Environment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    # -----------------------------
    # FIXED: VALID OPENENV TASK FORMAT
    # -----------------------------
    def get_tasks(self):
        return [
            Task(
                id=1,
                name="Study",
                priority=3,
                duration=2,
                deadline=10,
                energy="high",
                score=0.3
            ),
            Task(
                id=2,
                name="Workout",
                priority=1,
                duration=1,
                deadline=8,
                energy="medium",
                score=0.5
            ),
            Task(
                id=3,
                name="Project",
                priority=2,
                duration=3,
                deadline=15,
                energy="low",
                score=0.9
            ),
        ]


    # -----------------------------
    def _format_step(self, obs, reward, done):
        score = float(reward)

        # MUST be strictly inside (0,1)
        score = max(0.01, min(0.99, score))

        obs.reward = score
        obs.done = done

        return obs, score, done, {"score": score}

    # -----------------------------
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.tasks: List[Task] = []
        self.schedule = []
        self.current_time = 0
        self.done = False
        self.min_steps_required = 3

    # -----------------------------
    def reset(self) -> Hackathon2Observation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.done = False
        self.schedule = []
        self.current_time = 0

        self.tasks = [
            Task(
                id=1,
                name="Study",
                priority=3,
                duration=2,
                deadline=10,
                energy="high",
                score=0.3
            ),
            Task(
                id=2,
                name="Workout",
                priority=1,
                duration=1,
                deadline=8,
                energy="medium",
                score=0.5
            ),
            Task(
                id=3,
                name="Project",
                priority=2,
                duration=3,
                deadline=15,
                energy="low",
                score=0.9
            ),
        ]

        return Hackathon2Observation(
            message="Environment reset. Schedule tasks.",
            tasks=self.tasks,
            conflicts=[],
            reward=0.5,
            done=False,
            scheduled=[]
        )

    # -----------------------------
    def step(self, action):
        self._state.step_count += 1

        step_num = self._state.step_count
        done = step_num >= 3

        action_type = getattr(action, "action_type", "schedule")

        if action_type == "auto":
            action = self.auto_schedule()

        task = next((t for t in self.tasks if t.id == getattr(action, "task_id", None)), None)
        if not task and self.tasks:
            task = self.tasks[0]

        if not task:
            obs = Hackathon2Observation(
                message="No tasks left",
                tasks=[],
                conflicts=[],
                reward=0.5,
                done=True,
                scheduled=self.schedule
            )
            return self._format_step(obs, 0.5, True)

        start_time = getattr(action, "start_time", 0) or 0
        start_time = max(0, min(23, int(start_time)))
        end_time = start_time + 1

        self.schedule.append({
            "task_id": task.id,
            "name": task.name,
            "start": start_time,
            "end": end_time,
            "priority": task.priority
        })

        self.tasks = [t for t in self.tasks if t.id != task.id]

        # FIXED reward (strict 0–1 safe)
        # reward based on task properties (VALID GRADER STYLE)
        reward = (
            task.priority * 0.2 +
            (1.0 / (task.duration + 1)) * 0.3 +
            0.2
        )
        
        # ensure strict (0,1)
        reward = max(0.01, min(0.99, reward))

        self.done = done

        obs = Hackathon2Observation(
            message=f"Step {step_num} processed",
            tasks=self.tasks,
            conflicts=[],
            reward=reward,
            done=done,
            scheduled=self.schedule
        )

        return self._format_step(obs, reward, done)

    # -----------------------------
    def get_observation(self):
        return Hackathon2Observation(
            message="Current state",
            tasks=self.tasks,
            conflicts=[],
            reward=0.5,
            done=self.done,
            scheduled=self.schedule
        )

    @property
    def state(self):
        return self._state

    def get_state(self):
        return self._state

    def auto_schedule(self):
        if not self.tasks:
            return None

        task = self.tasks[0]

        class AutoAction:
            def __init__(self, task_id, start_time):
                self.task_id = task_id
                self.start_time = start_time

        return AutoAction(task.id, 0)

    def get_score(self):
        total_time = sum([s["end"] - s["start"] for s in self.schedule])
        score = sum([s["priority"] * 10 for s in self.schedule])
        idle_penalty = max(0, 24 - total_time)
        efficiency_score = max(0, score - idle_penalty * 2)

        return {
            "tasks_completed": len(self.schedule),
            "total_time_used": total_time,
            "idle_time": idle_penalty,
            "efficiency_score": efficiency_score
        }

    def get_schedule_visual(self):
        timeline = ["." for _ in range(24)]
        for task in self.schedule:
            for t in range(task["start"], task["end"]):
                timeline[t] = str(task["task_id"])
        return "".join(timeline)
