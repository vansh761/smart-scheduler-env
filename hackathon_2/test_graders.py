from models import Task
from grader import grade_easy, grade_medium, grade_hard

# Test data
tasks_easy = [Task(id=1, name="A", priority=3), Task(id=2, name="B", priority=1)]
tasks_medium = [Task(id=1, name="A", priority=3, start=1, end=3), Task(id=2, name="B", priority=1, start=2, end=4)]
tasks_hard = [Task(id=1, name="A", priority=3, start=1, end=3), Task(id=2, name="B", priority=1, start=4, end=5)]

print("Easy grader:", grade_easy(tasks_easy))      # Should be ~0.98 (sorted priorities)
print("Medium grader:", grade_medium(tasks_medium)) # Should be ~0.48 (conflict)
print("Hard grader:", grade_hard(tasks_hard))       # Should be ~0.9+ (no conflict, complete)
