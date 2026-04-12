def safe_score(score: float) -> float:
    score = float(score)
    if score <= 0.0:
        return 0.02
    if score >= 1.0:
        return 0.98
    return score

def grade_easy(trajectory):
    scheduled = []
    if isinstance(trajectory, dict):
        scheduled = trajectory.get("scheduled", []) or trajectory.get("tasks", [])
    elif hasattr(trajectory, "scheduled"):
        scheduled = trajectory.scheduled or []
    elif isinstance(trajectory, list):
        scheduled = trajectory

    if not scheduled:
        return 0.02

    priorities = [item.get("priority", 0) for item in scheduled if isinstance(item, dict)]
    if not priorities:
        return 0.02

    ordered = priorities == sorted(priorities, reverse=True)
    raw = 0.85 if ordered else 0.35
    return safe_score(raw)

def count_conflicts(scheduled):
    conflicts = 0
    for i in range(len(scheduled)):
        for j in range(i + 1, len(scheduled)):
            a = scheduled[i]
            b = scheduled[j]
            a_start, a_end = a.get("start", 0), a.get("end", 0)
            b_start, b_end = b.get("start", 0), b.get("end", 0)
            if not (a_end <= b_start or b_end <= a_start):
                conflicts += 1
    return conflicts

def extract_scheduled(trajectory):
    if isinstance(trajectory, dict):
        return trajectory.get("scheduled", []) or []
    if hasattr(trajectory, "scheduled"):
        return trajectory.scheduled or []
    if isinstance(trajectory, list):
        return trajectory
    return []

def grade_medium(trajectory):
    scheduled = extract_scheduled(trajectory)
    if not scheduled:
        return 0.02

    conflicts = count_conflicts(scheduled)
    raw = 0.8 - 0.2 * conflicts
    return safe_score(raw)

def grade_hard(trajectory):
    scheduled = extract_scheduled(trajectory)
    if not scheduled:
        return 0.02

    conflicts = count_conflicts(scheduled)
    total = len(scheduled)
    unique_tasks = len(set(item.get("task_id") for item in scheduled if isinstance(item, dict)))
    completeness = unique_tasks / max(total, 1)

    raw = 0.4 + 0.4 * completeness - 0.15 * conflicts
    return safe_score(raw)
