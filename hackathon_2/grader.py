def count_conflicts(tasks):
    conflicts = 0
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            t1, t2 = tasks[i], tasks[j]
            if t1.start and t2.start:
                if not (t1.end <= t2.start or t2.end <= t1.start):
                    conflicts += 1
    return conflicts


def safe_score(score: float) -> float:
    return max(0.02, min(0.98, score))

def grade_easy(tasks):
    priorities = [t.priority for t in tasks]
    raw = 0.98 if priorities == sorted(priorities) else 0.02
    return safe_score(raw)

def grade_medium(tasks):
    conflicts = count_conflicts(tasks)
    raw = 1.0 - 0.5 * conflicts
    return safe_score(raw)

def grade_hard(tasks):
    conflicts = count_conflicts(tasks)
    scheduled = [t for t in tasks if t.start is not None]
    completeness = len(scheduled) / len(tasks) if tasks else 0.0
    raw = (1 - conflicts * 0.3) + completeness * 0.5
    return safe_score(raw)
