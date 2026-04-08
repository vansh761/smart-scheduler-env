<<<<<<< HEAD
title: Smart Schedule Environment
emoji: 📅
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
Smart Schedule Environment
A real-world AI environment for task scheduling, conflict resolution, and optimization.

"This environment is compatible with reinforcement learning frameworks like Gym and can be used to train intelligent scheduling agents."

This environment is designed to train AI agents for real-world scheduling problems, including conflict resolution and priority optimization, making it directly applicable to productivity tools and AI assistants.

This environment simulates how humans manage daily schedules — prioritizing tasks, assigning time slots, resolving overlaps, and optimizing productivity.

🚀 Why This Environment Matters
Scheduling is a real-world problem faced by:

Students managing study + exams
Professionals handling meetings and deadlines
AI assistants like calendars (Google Calendar, Notion AI)
This environment allows AI agents to learn:

✔ Task prioritization
✔ Time allocation
✔ Conflict resolution
✔ Decision-making under constraints

🧠 Environment Overview
The agent is given a list of unscheduled tasks and must:

Assign time slots
Avoid conflicts
Respect priorities
Optimize the schedule
🎯 Tasks (Difficulty Levels)
🟢 Easy — Priority Sorting
Goal: Arrange tasks based on priority
Reward: Higher for correct ordering
🟡 Medium — Conflict Resolution
Goal: Schedule tasks without overlapping
Reward: Penalized for conflicts, rewarded for clean scheduling
🔴 Hard — Full Optimization
Goal: Create an optimal schedule considering:
Priority
Time allocation
No conflicts
Reward: Based on efficiency + correctness
⚙️ Action Space
Agent can perform:

schedule → Assign time to a task
move → Change task timing
delete → Remove task
finish → End scheduling
👀 Observation Space
Agent receives:

List of tasks (id, priority, start, end)
Conflict messages
Environment feedback message
🏆 Reward Design
Action	Reward
Valid scheduling	+0.2
Conflict resolution	+0.3
Optimal solution	+1.0
Conflict detected	-0.3
Invalid action	-0.2
✔ Provides dense reward signals
✔ Encourages learning step-by-step

🧪 Example Usage
from hackathon_2 import Hackathon2Env, Hackathon2Action

env = Hackathon2Env.from_docker_image("smart-schedule-env")

obs = env.reset()

action = Hackathon2Action(
    action_type="schedule",
    task_id=1,
    start=1,
    end=2
)

result = env.step(action)
print(result.observation.tasks)
=======
# smart-scheduler-env
>>>>>>> cda3fed9bcf67206a64949a8f3e56fa2c7a3a533
