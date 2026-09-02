# backend/scripts/seed_problems.py

from app.database import SessionLocal
from app.models.problem import Problem, Difficulty, ProblemType, ProblemSource

db = SessionLocal()

problems = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "difficulty": Difficulty.EASY,
        "problem_type": ProblemType.LEETCODE,
        "source": ProblemSource.MANUAL,
        "examples": "Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nExplanation: Because nums[0] + nums[1] == 9, we return [0, 1].",
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
        "tags": "array,hashmap",
        "starter_code_python": "def twoSum(nums, target):\n    # Write your code here\n    pass",
        "is_premium": False,
        "is_active": True
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.",
        "difficulty": Difficulty.EASY,
        "problem_type": ProblemType.LEETCODE,
        "source": ProblemSource.MANUAL,
        "examples": "Input: s = \"()\"\nOutput: true\n\nInput: s = \"()[]{}\"\nOutput: true\n\nInput: s = \"(]\"\nOutput: false",
        "constraints": "1 <= s.length <= 10^4\ns consists of parentheses only '()[]{}'.",
        "tags": "stack,string",
        "starter_code_python": "def isValid(s):\n    # Write your code here\n    pass",
        "is_premium": False,
        "is_active": True
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "difficulty": Difficulty.MEDIUM,
        "problem_type": ProblemType.LEETCODE,
        "source": ProblemSource.MANUAL,
        "examples": "Input: nums = [-2,1,-3,4,-1,2,1,-5,4]\nOutput: 6\nExplanation: The subarray [4,-1,2,1] has the largest sum 6.",
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "tags": "array,dynamic-programming,kadane",
        "starter_code_python": "def maxSubArray(nums):\n    # Write your code here\n    pass",
        "is_premium": False,
        "is_active": True
    }
]

for p in problems:
    existing = db.query(Problem).filter(Problem.slug == p["slug"]).first()
    if not existing:
        problem = Problem(**p)
        db.add(problem)
        print(f"Added: {p['title']}")
    else:
        print(f"Already exists: {p['title']}")

db.commit()
db.close()
print("\n✅ Sample problems seeded successfully!")