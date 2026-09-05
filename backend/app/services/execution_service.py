# backend/app/services/execution_service.py

import json
from sqlalchemy.orm import Session

from app.models.submission import Submission, SubmissionStatus
from app.models.test_result import TestResult
from app.models.problem_test_case import ProblemTestCase
from app.models.problem import Problem
from app.services.code_executor import code_executor


class ExecutionService:

    def execute_submission(
        self,
        submission: Submission,
        db: Session
    ) -> Submission:
        """Run submission against all test cases and save results."""

        # ==========================================
        # 1. Mark submission as RUNNING
        # ==========================================

        submission.status = SubmissionStatus.RUNNING
        db.commit()

        # ==========================================
        # 2. Get Problem
        # ==========================================

        problem = db.query(Problem).filter(
            Problem.id == submission.problem_id
        ).first()

        if not problem:
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.error_message = "Problem not found"

            db.commit()
            db.refresh(submission)

            return submission

        # Get function name from problem
        function_name = problem.function_name or "solve"

        # ==========================================
        # 3. Get Test Cases
        # ==========================================

        test_cases = db.query(ProblemTestCase).filter(
            ProblemTestCase.problem_id == submission.problem_id
        ).order_by(
            ProblemTestCase.order
        ).all()

        if not test_cases:
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.error_message = "No test cases found for this problem"
            submission.passed_count = 0
            submission.total_count = 0

            db.commit()
            db.refresh(submission)

            return submission

        # ==========================================
        # 4. Counters
        # ==========================================

        passed_count = 0
        total_time = 0.0

        has_runtime_error = False
        has_time_limit = False
        has_compilation_error = False

        # ==========================================
        # 5. Execute Every Test Case
        # ==========================================

        for tc in test_cases:

            # --------------------------------------
            # Parse input JSON
            # --------------------------------------

            try:
                input_dict = json.loads(tc.input_data)

            except Exception:
                input_dict = {}

            # --------------------------------------
            # Determine language
            # --------------------------------------

            language = submission.language.lower()

            # ======================================
            # Python Execution
            # ======================================

            if language in ["python", "python3"]:

                result = code_executor.run_python_function(
                    user_code=submission.code,
                    function_name=function_name,
                    input_data=input_dict
                )

            # ======================================
            # C++ Execution
            # ======================================

            elif language in ["cpp", "c++"]:

                result = code_executor.run_cpp_function(
                    user_code=submission.code,
                    function_name=function_name,
                    input_data=input_dict
                )

            # ======================================
            # Unsupported Language
            # ======================================

            else:

                result = {
                    "success": False,
                    "output": "",
                    "error": f"Language '{submission.language}' not supported",
                    "execution_time": 0
                }

            # ==========================================
            # 6. Add Execution Time
            # ==========================================
            print("========== EXECUTOR DEBUG ==========")
            print("LANGUAGE:", submission.language)
            print("RESULT:", result)
            print("RESULT TYPE:", type(result))
            print("====================================")
            total_time += result["execution_time"]

            # ==========================================
            # 7. Determine Test Case Result
            # ==========================================

            passed = False

            if result["success"]:

                passed = code_executor.compare_output(
                    result["output"],
                    tc.expected_output
                )

            else:

                error = result["error"] or ""

                if error == "Time Limit Exceeded":

                    has_time_limit = True

                elif error.startswith("Compilation Error"):

                    has_compilation_error = True

                else:

                    has_runtime_error = True

            # ==========================================
            # 8. Count Passed Tests
            # ==========================================

            if passed:
                passed_count += 1

            # ==========================================
            # 9. Save TestResult
            # ==========================================

            test_result = TestResult(
                submission_id=submission.id,
                test_case_id=tc.id,
                passed=passed,
                actual_output=result["output"] or None,
                expected_output=tc.expected_output,
                execution_time=result["execution_time"],
                error_message=result["error"]
            )

            db.add(test_result)

        # ==========================================
        # 10. Update Submission Summary
        # ==========================================

        submission.passed_count = passed_count
        submission.total_count = len(test_cases)

        submission.execution_time = round(
            total_time,
            4
        )

        # ==========================================
        # 11. Determine Final Submission Status
        # ==========================================

        if has_time_limit:

            submission.status = SubmissionStatus.TIME_LIMIT

            submission.error_message = (
                "Time Limit Exceeded on one or more test cases"
            )

        elif has_compilation_error:

            submission.status = SubmissionStatus.RUNTIME_ERROR

            submission.error_message = (
                "Compilation Error on one or more test cases"
            )

        elif has_runtime_error:

            submission.status = SubmissionStatus.RUNTIME_ERROR

            submission.error_message = (
                "Runtime error on one or more test cases"
            )

        else:

            submission.status = SubmissionStatus.COMPLETED
            submission.error_message = None

        # ==========================================
        # 12. Save Everything
        # ==========================================

        db.commit()
        db.refresh(submission)

        return submission


# Single instance
execution_service = ExecutionService()