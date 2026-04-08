# inference.py

import os
from typing import List
from hackathon_2 import Hackathon2Env, Hackathon2Action

API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")  # baseline

TASKS = [
    {"task_id": 1, "duration": 2, "priority": 3},
    {"task_id": 2, "duration": 1, "priority": 2},
    {"task_id": 3, "duration": 3, "priority": 1},
]

class InteractiveScheduler:
    def __init__(self):
        self.schedule = []  # list of scheduled tasks

    def is_conflict(self, start, end):
        for task in self.schedule:
            if not (end <= task["start"] or start >= task["end"]):
                return True
        return False

    def available_slots(self, duration, earliest=0, latest=24):
        """Return list of available start times for a given duration"""
        slots = []
        for t in range(earliest, latest - duration + 1):
            if not self.is_conflict(t, t + duration):
                slots.append(t)
        return slots

    def add_task(self, task_id, duration, preferred_start):
        if self.is_conflict(preferred_start, preferred_start + duration):
            print(f"⚠ Conflict detected for Task {task_id} at {preferred_start}-{preferred_start + duration}")
            slots = self.available_slots(duration)
            if not slots:
                print("❌ No available slots. Task skipped.")
                return None, -1, True
            print(f"Available slots: {slots}")
            chosen = int(input(f"Choose a start time from available slots for Task {task_id}: "))
        else:
            chosen = preferred_start

        end = chosen + duration
        reward = 10  # base reward
        reward += 5  # priority bonus
        reward += max(0, 10 - chosen)  # efficiency bonus
        self.schedule.append({
            "task_id": task_id,
            "start": chosen,
            "end": end
        })
        print(f"✅ Task {task_id} scheduled at {chosen}-{end}")
        return chosen, reward, False


def main():
    env = Hackathon2Env.from_docker_image("smart-schedule-env")
    scheduler = InteractiveScheduler()
    rewards = []

    print(f"[START] task=smart-schedule env=hackathon_2 model={MODEL_NAME}")

    obs = env.reset()
    done = False
    step_num = 0

    for task in TASKS:
        if done:
            break
        preferred_start = 0
        start, reward, skipped = scheduler.add_task(task["task_id"], task["duration"], preferred_start)
        if skipped:
            continue

        action = Hackathon2Action(
            action_type="schedule",
            task_id=task["task_id"],
            start=start,
            end=start + task["duration"]
        )
        result = env.step(action)
        rewards.append(result.reward)
        step_num += 1
        print(
            f"[STEP] step={step_num} action=schedule(task_id={task['task_id']}) "
            f"reward={result.reward:.2f} done={result.done} error={result.error or 'null'}"
        )
        done = result.done

    print(
        f"[END] success={not done} steps={step_num} score={sum(rewards)/len(rewards):.2f} "
        f"rewards={','.join(f'{r:.2f}' for r in rewards)}"
    )


if __name__ == "__main__":
    main()