# backend/scripts/seed_test_cases.py

from app.database import SessionLocal
from app.models.problem_test_case import ProblemTestCase

db = SessionLocal()

test_cases = [
    {
        "problem_id": 1,
        "input_data": '{"nums": [2, 7, 11, 15], "target": 9}',
        "expected_output": "[0, 1]",
        "is_hidden": False,
        "order": 1,
        "explanation": "Basic example"
    },
    {
        "problem_id": 1,
        "input_data": '{"nums": [3, 2, 4], "target": 6}',
        "expected_output": "[1, 2]",
        "is_hidden": False,
        "order": 2,
        "explanation": "Another common case"
    },
    {
        "problem_id": 1,
        "input_data": '{"nums": [3, 3], "target": 6}',
        "expected_output": "[0, 1]",
        "is_hidden": True,
        "order": 3,
        "explanation": "Hidden test case - duplicates"
    }
]

for tc in test_cases:
    existing = db.query(ProblemTestCase).filter(
        ProblemTestCase.problem_id == tc["problem_id"],
        ProblemTestCase.order == tc["order"]
    ).first()
    
    if not existing:
        db.add(ProblemTestCase(**tc))
        print(f"Added test case order {tc['order']}")
    else:
        print(f"Already exists: order {tc['order']}")

db.commit()
db.close()
print("\n✅ Test cases seeded!")