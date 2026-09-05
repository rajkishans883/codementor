# backend/app/services/code_executor.py

import subprocess
import tempfile
import os
import json
import time
from typing import Dict, Any


class CodeExecutor:
    """Safe code execution service (V1 - Python + C++)"""

    TIMEOUT_SECONDS = 5

    # =========================================================
    # PYTHON EXECUTION
    # =========================================================

    def run_python_function(
        self,
        user_code: str,
        function_name: str,
        input_data: dict
    ) -> Dict[str, Any]:
        """
        Run LeetCode-style Python function inside Docker.

        Example user code:

        def twoSum(nums, target):
            return [0, 1]
        """

        args_json = json.dumps(input_data)

        # IMPORTANT:
        # Wrapper must start from column 0.
        # User code is inserted without changing its indentation.

        wrapper_code = f"""import json
import sys

# ===== USER CODE START =====
{user_code}
# ===== USER CODE END =====

if __name__ == "__main__":
    try:
        args = json.loads({repr(args_json)})
        result = {function_name}(**args)
        print(json.dumps(result))

    except Exception as e:
        print("ERROR:" + str(e), file=sys.stderr)
        sys.exit(1)
"""

        temp_dir = None

        try:
            # =================================================
            # CREATE TEMPORARY DIRECTORY
            # =================================================

            temp_dir = tempfile.mkdtemp()

            code_path = os.path.join(
                temp_dir,
                "main.py"
            )

            # =================================================
            # WRITE GENERATED PYTHON FILE
            # =================================================

            with open(code_path, "w", encoding="utf-8") as file:
                file.write(wrapper_code)

            # =================================================
            # RUN PYTHON CODE INSIDE DOCKER
            # =================================================

            start_time = time.time()

            docker_result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",

                    # Disable internet access
                    "--network",
                    "none",

                    # Memory limit
                    "--memory",
                    "128m",

                    # CPU limit
                    "--cpus",
                    "0.5",

                    # Process limit
                    "--pids-limit",
                    "64",

                    # Mount generated code as read-only
                    "-v",
                    f"{temp_dir}:/code:ro",

                    # Docker image
                    "codementor-python",

                    # Execute Python file
                    "python3",
                    "/code/main.py"
                ],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS + 5
            )

            execution_time = time.time() - start_time

            # =================================================
            # SUCCESSFUL EXECUTION
            # =================================================

            if docker_result.returncode == 0:
                return {
                    "success": True,
                    "output": docker_result.stdout.strip(),
                    "error": None,
                    "execution_time": round(
                        execution_time,
                        4
                    )
                }

            # =================================================
            # PYTHON RUNTIME / SYNTAX ERROR
            # =================================================

            error_msg = docker_result.stderr.strip()

            if "ERROR:" in error_msg:
                error_msg = error_msg.split(
                    "ERROR:",
                    1
                )[1].strip()

            # IMPORTANT:
            # This return is outside the if block.
            # Therefore it always returns a dictionary.
            return {
                "success": False,
                "output": docker_result.stdout.strip(),
                "error": error_msg or "Runtime Error",
                "execution_time": round(
                    execution_time,
                    4
                )
            }

        # =====================================================
        # TIME LIMIT EXCEEDED
        # =====================================================

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Time Limit Exceeded",
                "execution_time": self.TIMEOUT_SECONDS
            }

        # =====================================================
        # DOCKER / OTHER EXECUTION ERROR
        # =====================================================

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }

        # =====================================================
        # CLEANUP TEMPORARY DIRECTORY
        # =====================================================

        finally:
            if temp_dir and os.path.exists(temp_dir):

                for name in os.listdir(temp_dir):
                    path = os.path.join(
                        temp_dir,
                        name
                    )

                    try:
                        os.remove(path)
                    except Exception:
                        pass

                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

    # =========================================================
    # C++ EXECUTION
    # =========================================================

    def run_cpp_function(
        self,
        user_code: str,
        function_name: str,
        input_data: dict
    ) -> Dict[str, Any]:
        """
        Run LeetCode-style C++ function inside Docker.

        V1 currently supports input like:

        {
            "nums": [2, 7, 11, 15],
            "target": 9
        }
        """

        nums = input_data.get("nums", [])
        target = input_data.get("target", 0)

        nums_str = ",".join(
            str(number)
            for number in nums
        )

        wrapper_code = f"""#include <bits/stdc++.h>
using namespace std;

// ===== USER CODE START =====
{user_code}
// ===== USER CODE END =====

int main() {{
    try {{
        vector<int> nums = {{{nums_str}}};
        int target = {target};

        vector<int> result = {function_name}(nums, target);

        cout << "[";

        for (int i = 0; i < (int)result.size(); i++) {{
            cout << result[i];

            if (i + 1 < (int)result.size()) {{
                cout << ", ";
            }}
        }}

        cout << "]";

        return 0;
    }}
    catch (exception &e) {{
        cerr << "ERROR:" << e.what();
        return 1;
    }}
}}
"""

        temp_dir = None

        try:
            # =================================================
            # CREATE TEMPORARY DIRECTORY
            # =================================================

            temp_dir = tempfile.mkdtemp()

            cpp_path = os.path.join(
                temp_dir,
                "main.cpp"
            )

            # =================================================
            # WRITE GENERATED C++ FILE
            # =================================================

            with open(cpp_path, "w", encoding="utf-8") as file:
                file.write(wrapper_code)

            # =================================================
            # COMPILE AND RUN INSIDE DOCKER
            # =================================================

            start_time = time.time()

            docker_result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",

                    # Disable internet
                    "--network",
                    "none",

                    # Memory limit
                    "--memory",
                    "256m",

                    # CPU limit
                    "--cpus",
                    "0.5",

                    # Process limit
                    "--pids-limit",
                    "64",

                    # Mount code directory
                    "-v",
                    f"{temp_dir}:/code",

                    # Docker image
                    "codementor-cpp",

                    # Compile and execute
                    "bash",
                    "-c",
                    (
                        "g++ -std=c++17 -O2 "
                        "/code/main.cpp "
                        "-o /code/main.out "
                        "&& /code/main.out"
                    )
                ],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS + 10
            )

            execution_time = time.time() - start_time

            # =================================================
            # SUCCESSFUL EXECUTION
            # =================================================

            if docker_result.returncode == 0:
                return {
                    "success": True,
                    "output": docker_result.stdout.strip(),
                    "error": None,
                    "execution_time": round(
                        execution_time,
                        4
                    )
                }

            # =================================================
            # COMPILATION / RUNTIME ERROR
            # =================================================

            error_msg = docker_result.stderr.strip()

            if "ERROR:" in error_msg:
                error_msg = error_msg.split(
                    "ERROR:",
                    1
                )[1].strip()

            return {
                "success": False,
                "output": docker_result.stdout.strip(),
                "error": error_msg or "Compilation/Runtime Error",
                "execution_time": round(
                    execution_time,
                    4
                )
            }

        # =====================================================
        # TIME LIMIT EXCEEDED
        # =====================================================

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Time Limit Exceeded",
                "execution_time": self.TIMEOUT_SECONDS
            }

        # =====================================================
        # OTHER EXECUTION ERROR
        # =====================================================

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }

        # =====================================================
        # CLEANUP
        # =====================================================

        finally:
            if temp_dir and os.path.exists(temp_dir):

                for name in os.listdir(temp_dir):
                    path = os.path.join(
                        temp_dir,
                        name
                    )

                    try:
                        os.remove(path)
                    except Exception:
                        pass

                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

    # =========================================================
    # OUTPUT COMPARISON
    # =========================================================

    def compare_output(
        self,
        actual: str,
        expected: str
    ) -> bool:
        """
        Compare actual and expected output.

        First tries JSON comparison.
        If JSON parsing fails, compares normalized strings.
        """

        try:
            actual_parsed = json.loads(actual)
            expected_parsed = json.loads(expected)

            return actual_parsed == expected_parsed

        except Exception:
            actual_clean = " ".join(
                (actual or "").strip().split()
            )

            expected_clean = " ".join(
                (expected or "").strip().split()
            )

            return actual_clean == expected_clean


# =============================================================
# SINGLETON INSTANCE
# =============================================================

code_executor = CodeExecutor()











































































































# # backend/app/services/code_executor.py

# import subprocess
# import tempfile
# import os
# import json
# import time
# import textwrap
# from typing import Dict, Any


# class CodeExecutor:
#     """Safe code execution service (V1 - Python + C++)"""

#     TIMEOUT_SECONDS = 5

#     def run_python_function(
#                 self,
#                 user_code: str,
#                 function_name: str,
#                 input_data: dict
#             ) -> Dict[str, Any]:
#         """Run LeetCode-style Python function inside Docker."""

#         args_json = json.dumps(input_data)

#         # IMPORTANT:
#         # Do NOT indent user_code.
#         # User code must remain exactly as submitted.

#         wrapper_code = f"""import json
#             import sys

#             # ===== USER CODE START =====
#             {user_code}
#             # ===== USER CODE END =====

#             if __name__ == "__main__":
#                 try:
#                     args = json.loads({repr(args_json)})
#                     result = {function_name}(**args)
#                     print(json.dumps(result))
#                 except Exception as e:
#                     print("ERROR:" + str(e), file=sys.stderr)
#                     sys.exit(1)
#             """

#         temp_dir = None

#         try:

#             # ==========================================
#             # Create temporary directory
#             # ==========================================

#             temp_dir = tempfile.mkdtemp()

#             code_path = os.path.join(
#                 temp_dir,
#                 "main.py"
#             )

#             # ==========================================
#             # Write generated Python file
#             # ==========================================

#             with open(code_path, "w") as f:
#                 f.write(wrapper_code)

#             # ==========================================
#             # Run inside Docker
#             # ==========================================

#             start_time = time.time()

#             result = subprocess.run(
#                 [
#                     "docker",
#                     "run",
#                     "--rm",

#                     # No internet
#                     "--network",
#                     "none",

#                     # Memory limit
#                     "--memory",
#                     "128m",

#                     # CPU limit
#                     "--cpus",
#                     "0.5",

#                     # Process limit
#                     "--pids-limit",
#                     "64",

#                     # Mount code read-only
#                     "-v",
#                     f"{temp_dir}:/code:ro",

#                     # Docker image
#                     "codementor-python",

#                     # Execute
#                     "python3",
#                     "/code/main.py"
#                 ],
#                 capture_output=True,
#                 text=True,
#                 timeout=self.TIMEOUT_SECONDS + 5
#             )

#             execution_time = time.time() - start_time

#             # ==========================================
#             # Successful execution
#             # ==========================================

#             if result.returncode == 0:

#                 return {
#                     "success": True,
#                     "output": result.stdout.strip(),
#                     "error": None,
#                     "execution_time": round(
#                         execution_time,
#                         4
#                     )
#                 }

#             # ==========================================
#             # Runtime / Python error
#             # ==========================================

#             error_msg = result.stderr.strip()

#             if "ERROR:" in error_msg:
#                 error_msg = error_msg.split(
#                     "ERROR:",
#                     1
#                 )[1].strip()

#             return {
#                 "success": False,
#                 "output": result.stdout.strip(),
#                 "error": error_msg or "Runtime Error",
#                 "execution_time": round(
#                     execution_time,
#                     4
#                 )
#             }

#         # ==============================================
#         # Timeout
#         # ==============================================

#         except subprocess.TimeoutExpired:

#             return {
#                 "success": False,
#                 "output": "",
#                 "error": "Time Limit Exceeded",
#                 "execution_time": self.TIMEOUT_SECONDS
#             }

#         # ==============================================
#         # Other execution error
#         # ==============================================

#         except Exception as e:

#             return {
#                 "success": False,
#                 "output": "",
#                 "error": str(e),
#                 "execution_time": 0
#             }

#         # ==============================================
#         # Cleanup
#         # ==============================================

#         finally:

#             if temp_dir and os.path.exists(temp_dir):

#                 for name in os.listdir(temp_dir):

#                     path = os.path.join(
#                         temp_dir,
#                         name
#                     )

#                     try:
#                         os.remove(path)
#                     except Exception:
#                         pass

#                 try:
#                     os.rmdir(temp_dir)
#                 except Exception:
#                     pass


#     def run_cpp_function(
#             self,
#             user_code: str,
#             function_name: str,
#             input_data: dict
#                 ) -> Dict[str, Any]:
#         """
#         Run LeetCode-style C++ function inside Docker.
#         V1 supports: {"nums":[...], "target": ...}
#         """

#         nums = input_data.get("nums", [])
#         target = input_data.get("target", 0)
#         nums_str = ",".join(str(x) for x in nums)

#         wrapper_code = textwrap.dedent(f"""\
#             #include <bits/stdc++.h>
#             using namespace std;

#             // ===== USER CODE START =====
#             {user_code}
#             // ===== USER CODE END =====

#             int main() {{
#                 try {{
#                     vector<int> nums = {{{nums_str}}};
#                     int target = {target};
#                     vector<int> result = {function_name}(nums, target);

#                     cout << "[";
#                     for (int i = 0; i < (int)result.size(); i++) {{
#                         cout << result[i];
#                         if (i + 1 < (int)result.size()) cout << ", ";
#                     }}
#                     cout << "]";
#                     return 0;
#                 }} catch (exception &e) {{
#                     cerr << "ERROR:" << e.what();
#                     return 1;
#                 }}
#             }}
#             """)

#         temp_dir = None
#         try:
#             temp_dir = tempfile.mkdtemp()
#             cpp_path = os.path.join(temp_dir, "main.cpp")
#             with open(cpp_path, "w") as f:
#                 f.write(wrapper_code)

#             start_time = time.time()

#             # Compile + run inside one container
#             result = subprocess.run(
#                 [
#                     "docker", "run", "--rm",
#                     "--network", "none",
#                     "--memory", "256m",
#                     "--cpus", "0.5",
#                     "--pids-limit", "64",
#                     "-v", f"{temp_dir}:/code",
#                     "codementor-cpp",
#                     "bash", "-c",
#                     "g++ -std=c++17 -O2 /code/main.cpp -o /code/main.out && /code/main.out"
#                 ],
#                 capture_output=True,
#                 text=True,
#                 timeout=self.TIMEOUT_SECONDS + 10
#             )
#             execution_time = time.time() - start_time

#             if result.returncode == 0:
#                 return {
#                     "success": True,
#                     "output": result.stdout.strip(),
#                     "error": None,
#                     "execution_time": round(execution_time, 4)
#                 }

#             error_msg = result.stderr.strip()
#             if "ERROR:" in error_msg:
#                 error_msg = error_msg.split("ERROR:")[-1].strip()

#             return {
#                 "success": False,
#                 "output": result.stdout.strip(),
#                 "error": error_msg or "Compilation/Runtime Error",
#                 "execution_time": round(execution_time, 4)
#             }

#         except subprocess.TimeoutExpired:
#             return {
#                 "success": False,
#                 "output": "",
#                 "error": "Time Limit Exceeded",
#                 "execution_time": self.TIMEOUT_SECONDS
#             }
#         except Exception as e:
#             return {
#                 "success": False,
#                 "output": "",
#                 "error": str(e),
#                 "execution_time": 0
#             }
#         finally:
#             if temp_dir and os.path.exists(temp_dir):
#                 for name in os.listdir(temp_dir):
#                     try:
#                         os.remove(os.path.join(temp_dir, name))
#                     except Exception:
#                         pass
#                 os.rmdir(temp_dir)


#     def compare_output(self, actual: str, expected: str) -> bool:
#         """Compare actual vs expected output (JSON-aware)"""
#         try:
#             actual_parsed = json.loads(actual)
#             expected_parsed = json.loads(expected)
#             return actual_parsed == expected_parsed
#         except Exception:
#             actual_clean = " ".join((actual or "").strip().split())
#             expected_clean = " ".join((expected or "").strip().split())
#             return actual_clean == expected_clean


# code_executor = CodeExecutor()