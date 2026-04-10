import os
import traceback
from openai import OpenAI
from hackathon_2 import Hackathon2Env, Hackathon2Action

# ✅ Use validator-provided API
MODEL_NAME = "gpt-4.1-mini"

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

TASKS = [
    {"task_id": 1, "duration": 2, "priority": 3},
    {"task_id": 2, "duration": 1, "priority": 2},
    {"task_id": 3, "duration": 3, "priority": 1},
]

class InteractiveScheduler:
    def __init__(self):
        self.schedule = []

    def is_conflict(self, start, end):
        for task in self.schedule:
            if not (end <= task["start"] or start >= task["end"]):
                return True
        return False

    def available_slots(self, duration, earliest=0, latest=24):
        slots = []
        for t in range(earliest, latest - duration + 1):
            if not self.is_conflict(t, t + duration):
                slots.append(t)
        return slots

    def add_task(self, task_id, duration, preferred_start):
        if self.is_conflict(preferred_start, preferred_start + duration):
            slots = self.available_slots(duration)
            if not slots:
                return None, -1, True
            chosen = slots[0]
        else:
            chosen = preferred_start

        end = chosen + duration
        reward = 10 + 5 + max(0, 10 - chosen)
        self.schedule.append({"task_id": task_id, "start": chosen, "end": end})
        return chosen, reward, False

def run_inference(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception:
        return "error"

def main():
    task_name = "smart-schedule"
    benchmark = "hackathon_2"
    success = False
    rewards = []
    steps = 0

    print(f"[START] task={task_name} env={benchmark} model={MODEL_NAME}")

    try:
        env = Hackathon2Env(base_url="http://localhost:7860")

        scheduler = InteractiveScheduler()

        obs = env.reset()
        done = False

        for task in TASKS:
            if done:
                break

            # ✅ LLM decides best start time
            prompt = f"""
You are a smart scheduling AI.

Task:
- task_id: {task['task_id']}
- duration: {task['duration']}
- priority: {task['priority']}

Already scheduled tasks:
{scheduler.schedule}

Return ONLY a single integer start time (0-23).
No explanation.
"""
            llm_output = run_inference(prompt)

            # ✅ Safe extraction of number
            try:
                preferred_start = int(''.join(filter(str.isdigit, llm_output)))
                if preferred_start < 0 or preferred_start > 23:
                    preferred_start = 0
            except:
                preferred_start = 0

            # ✅ Your original logic (unchanged)
            start, reward, skipped = scheduler.add_task(
                task["task_id"], task["duration"], preferred_start
            )

            if skipped:
                continue

            action = Hackathon2Action(
                action_type="schedule",
                task_id=task["task_id"],
                start=start,
                end=start + task["duration"]
            )

            try:
                result = env.step(action)

                if isinstance(result, tuple):
                    obs_step, r, done, info = result
                else:
                    obs_step = result
                    r = getattr(result, "reward", reward)
                    done = getattr(result, "done", False)
                    info = getattr(result, "error", None)

                rewards.append(r)
                steps += 1

                print(
                    f"[STEP] step={steps} action=schedule(task_id={task['task_id']}) "
                    f"reward={r:.2f} done={str(done).lower()} error={info if info else 'null'}"
                )

            except Exception as e_step:
                steps += 1
                rewards.append(0.0)
                print(
                    f"[STEP] step={steps} action=error "
                    f"reward=0.00 done=false error={str(e_step)}"
                )
                done = True

        success = not done

    except Exception as e:
        print(
            f"[STEP] step={steps + 1} action=error "
            f"reward=0.00 done=false error={str(e)}"
        )
        success = False

    finally:
        print(
            f"[END] success={str(success).lower()} steps={steps} "
            f"rewards={','.join(f'{r:.2f}' for r in rewards)}"
        )

if __name__ == "__main__":
    main()
