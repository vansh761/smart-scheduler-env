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
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.done = False
        self.schedule = []
        self.current_time = 0

        dynamic_tasks = [
            Task(
                id=5+i,
                name=f"Task-{i}",
                priority=random.randint(1,3),
                start=None,
                end=None,
                duration=random.randint(1,3),
                deadline=random.randint(5,15),
                energy=random.choice(["low","medium","high"]),
                depends_on=random.choice([None] + [t.id for t in self.tasks] if self.tasks else [None])
            )
            for i in range(3)
        ]

        self.tasks.extend(dynamic_tasks)

        self.tasks = [
            Task(id=1, name="Study", priority=3, start=None, end=None, duration=2, deadline=10, energy="high", depends_on=None),
            Task(id=2, name="Workout", priority=1, start=None, end=None, duration=1, deadline=8, energy="medium", depends_on=None),
            Task(id=3, name="Project", priority=2, start=None, end=None, duration=3, deadline=15, energy="low", depends_on=None),
            Task(id=4, name="Meeting", priority=1, start=None, end=None, duration=1, deadline=12, energy="medium", depends_on=None),
        ]

        obs = Hackathon2Observation(
            message="Environment reset. Schedule tasks.",
            tasks=self.tasks,
            conflicts=[],
            done=False,
            reward=0.5,  # FIXED
            scheduled=[{
                "task_id": s["task_id"],
                "start": s["start"],
                "end": s.get("end", s["start"] + 1),
                "priority": s["priority"]
            } for s in self.schedule]
        )
        return self._format_step(obs,10,False)

    def step(self, action):
        reward = 0
        done = False
        info = {}
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
            return self._format_step(obs,10,False)

        if action_type == "move":
            for s in self.schedule:
                if s["task_id"] == action.task_id:
                    duration = s["end"] - s["start"]
                    new_start = action.start
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
                    return self._format_step(obs,10,False)

        if action_type == "delete":
            self.schedule = [s for s in self.schedule if s["task_id"] != action.task_id]

            obs = Hackathon2Observation(
                message="Task deleted",
                tasks=self.tasks,
                conflicts=[],
                reward=0.2,
                done=False,
                scheduled=self.schedule
            )
            return self._format_step(obs,10,False)

        if action_type == "move":
            existing = next((s for s in self.schedule if s["task_id"] == action.task_id), None)

            if existing:
                duration = existing["end"] - existing["start"]
                start_time = getattr(action, "start_time", existing["start"])
                existing["start"] = start_time
                existing["end"] = start_time + duration
                existing["priority"] = getattr(action, "priority", existing["priority"])
                existing["name"] = getattr(action, "name", existing.get("name", "Task"))

                obs = Hackathon2Observation(
                    message="Task moved successfully",
                    tasks=self.tasks,
                    conflicts=[],
                    reward=0.3,
                    done=False,
                    scheduled=self.schedule
                )
                return self._format_step(obs,10,False)

        if getattr(action, "task_id", None) == -1:
            action = self.auto_schedule()
            if action is None:
                obs = Hackathon2Observation(
                    message="No valid actions left.",
                    tasks=self.tasks,
                    conflicts=["No valid actions left."],
                    reward=0.2,
                    done=False,
                    scheduled=self.schedule
                )
                return self._format_step(obs,10,False)

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
            return self._format_step(obs,10,False)

        if any(s["task_id"] == action.task_id for s in self.schedule):
            obs Hackathon2Observation(
                message="Task already completed",
                tasks=self.tasks,
                conflicts=["Task already completed"],
                reward=0.2,
                done=False,
                scheduled=self.schedule
            )
            return self._format_step(obs,10,False)

        duration = getattr(task, "duration", 1)
        deadline = getattr(task, "deadline", 24)
        energy = getattr(task, "energy", "medium")
        depends_on = getattr(task, "depends_on", None)

        start_time = getattr(action, "start_time", getattr(action, "start", 0))
        end_time = start_time + duration

        priority = getattr(action, "priority", task.priority)
        name = getattr(action, "name", task.name)

        if depends_on is not None:
            dep_task = next((s for s in self.schedule if s["task_id"] == depends_on), None)
            if not dep_task:
                obs = Hackathon2Observation(
                    message="Dependency not met",
                    tasks=self.tasks,
                    conflicts=[f"Task {task.id} depends on task {depends_on}"],
                    reward=0.2,
                    done=False,
                    scheduled=self.schedule
                )
                return self._format_step(obs,10,False)

        for s in self.schedule:
            s_end = s["end"]  # FIXED
            if not (end_time <= s["start"] or start_time >= s_end):
                obs = Hackathon2Observation(
                    message="Time overlap",
                    tasks=self.tasks,
                    conflicts=["Time overlap"],
                    reward=0.2,
                    done=False,
                    scheduled=self.schedule
                )
                return self._format_step(obs,10,False)

        reward += 10 if end_time <= deadline else -min(10, end_time - deadline)
        reward += priority * 5

        if energy == "high" and 0 <= start_time <= 5:
            reward += 5
        elif energy == "medium" and 3 <= start_time <= 8:
            reward += 3
        elif energy == "low" and start_time >= 6:
            reward += 2

        reward += max(0, 5 - start_time * 0.5)

        gap = start_time - self.current_time
        if gap > 0:
            reward -= min(5, gap * 0.5)

        self.schedule.append({
            "task_id": task.id,
            "name": name,
            "start": start_time,
            "end": end_time,  # FIXED
            "priority": priority
        })

        self.current_time = max(self.current_time, end_time)
        self.tasks = [t for t in self.tasks if t.id != task.id]

        if not self.tasks:
            done = True

        self.done = done

        # ✅ NORMALIZATION
        score = reward / 50
        score = max(0.01, min(0.99, score))

        obs = Hackathon2Observation(
            message="Action processed",
            tasks=self.tasks,
            conflicts=[],
            reward=score,
            done=done,
            scheduled=self.schedule
        )

        info = {"score": score}

        return obs, score, done, info

    def get_observation(self):
        obs = Hackathon2Observation(
            message="Current state",
            tasks=self.tasks,
            conflicts=[],
            scheduled=self.schedule
        )
        return self._format_step(obs,10,False)

    @property
    def state(self):
        return self._state

    def get_state(self):
        return self._state

    def auto_schedule(self):
        best_task = None
        best_score = -999
        best_start = 0

        if random.random() < 0.1:
            urgent_task = Task(
                id=100,
                name="Urgent",
                priority=5,
                start=None,
                end=None,
                duration=1,
                deadline=self.current_time+2,
                energy="high",
                depends_on=None
            )
            self.tasks.append(urgent_task)

        for task in self.tasks:
            duration = getattr(task, "duration", 1)

            for start in range(0, 24):
                end = start + duration

                overlap = any(not (end <= s["start"] or start >= s["end"]) for s in self.schedule)
                if overlap:
                    continue

                score = task.priority * 10

                if score > best_score:
                    best_score = score
                    best_task = task
                    best_start = start

        if best_task is None:
            return None

        class AutoAction:
            def __init__(self, task_id, start_time):
                self.task_id = task_id
                self.start_time = start_time

        return AutoAction(best_task.id, best_start)

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
