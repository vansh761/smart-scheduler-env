def count_conflicts(tasks):
    conflicts = 0
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            t1, t2 = tasks[i], tasks[j]
            if t1.start and t2.start:
                if not (t1.end <= t2.start or t2.end <= t1.start):
                    conflicts += 1
    return conflicts


def grade_easy(tasks):
    priorities = [t.priority for t in tasks]
    return 1.0 if priorities == sorted(priorities) else 0.0


def grade_medium(tasks):
    conflicts = count_conflicts(tasks)
    return max(0.0, 1.0 - 0.5 * conflicts)


def grade_hard(tasks):
    conflicts = count_conflicts(tasks)

    scheduled = [t for t in tasks if t.start is not None]
    completeness = len(scheduled) / len(tasks)

    score = 0.0
    score += (1 - conflicts * 0.3)
    score += completeness * 0.5

    return max(0.0, min(1.0, score))