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

    def _format_step(self, obs, reward, done):
        score = reward / 50
        score = max(0.01, min(0.99, score))

        obs.reward = score
        obs.done = done

        info = {"score": score}

        return obs, score, done, info

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.tasks: List[Task] = []
        self.schedule = []
        self.current_time = 0
        self.done = False

    def reset(self) -> Hackathon2Observation:
        # ✅ FIXED INDENTATION
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.done = False
        self.schedule = []
        self.current_time = 0

        # ✅ FIXED TASK MODEL (only allowed fields)
        self.tasks = [
            Task(id=1, name="Study", priority=3, start=None, energy="high"),
            Task(id=2, name="Workout", priority=1, start=None, energy="medium"),
            Task(id=3, name="Project", priority=2, start=None, energy="low"),
            Task(id=4, name="Meeting", priority=1, start=None, energy="medium"),
        ]

        return Hackathon2Observation(
            message="Environment reset. Schedule tasks.",
            tasks=self.tasks,
            conflicts=[],
            reward=0.5,
            done=False,
            scheduled=[]
        )

    def step(self, action):
        reward = 0
        done = False
        self._state.step_count += 1

        if not self.tasks:
            self.reset()

        action_type = getattr(action, "action_type", "schedule")

        if action_type == "auto":
            action = self.auto_schedule()

        if action_type == "delete":
            self.schedule = [s for s in self.schedule if s["task_id"] != action.task_id]

            obs = Hackathon2Observation(
                message=f"Task {action.task_id} deleted",
                tasks=self.tasks,
                conflicts=[],
                reward=0.2,
                done=False,
                scheduled=self.schedule
            )
            return self._format_step(obs, 10, False)

        if action_type == "move":
            for s in self.schedule:
                if s["task_id"] == action.task_id:
                    duration = s["end"] - s["start"]
                    new_start = action.start_time or s["start"]
                    new_end = new_start + duration

                    self.schedule.remove(s)

                    self.schedule.append({
                        "task_id": s["task_id"],
                        "start": new_start,
                        "end": new_end,
                        "priority": s["priority"]
                    })

                    obs = Hackathon2Observation(
                        message=f"Task {action.task_id} moved",
                        tasks=self.tasks,
                        conflicts=[],
                        reward=0.3,
                        done=False,
                        scheduled=self.schedule
                    )
                    return self._format_step(obs, 10, False)

        task = next((t for t in self.tasks if t.id == action.task_id), None)

        if not task:
            obs = Hackathon2Observation(
                message="Invalid task",
                tasks=self.tasks,
                conflicts=["Invalid task"],
                reward=0.2,
                done=False,
                scheduled=self.schedule
            )
            return self._format_step(obs, 10, False)

        if any(s["task_id"] == action.task_id for s in self.schedule):
            obs = Hackathon2Observation(
                message="Task already completed",
                tasks=self.tasks,
                conflicts=["Task already completed"],
                reward=0.2,
                done=False,
                scheduled=self.schedule
            )
            return self._format_step(obs, 10, False)

        start_time = getattr(action, "start_time", 0)
        end_time = start_time + 1  # simple duration

        # overlap check
        for s in self.schedule:
            if not (end_time <= s["start"] or start_time >= s["end"]):
                obs = Hackathon2Observation(
                    message="Time overlap",
                    tasks=self.tasks,
                    conflicts=["Time overlap"],
                    reward=0.2,
                    done=False,
                    scheduled=self.schedule
                )
                return self._format_step(obs, 10, False)

        reward += 10 + task.priority * 5

        self.schedule.append({
            "task_id": task.id,
            "name": task.name,
            "start": start_time,
            "end": end_time,
            "priority": task.priority
        })

        self.tasks = [t for t in self.tasks if t.id != task.id]

        if not self.tasks:
            done = True

        self.done = done

        obs = Hackathon2Observation(
            message="Action processed",
            tasks=self.tasks,
            conflicts=[],
            reward=0.5,
            done=done,
            scheduled=self.schedule
        )

        return self._format_step(obs, reward, done)

    def get_observation(self):
        return Hackathon2Observation(
            message="Current state",
            tasks=self.tasks,
            conflicts=[],
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
        score = sum([s["priority"]*10 for s in self.schedule])
        idle_penalty = max(0, 24 - total_time)
        efficiency_score = max(0, score - idle_penalty*2)

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
