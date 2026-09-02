from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from requests import session

from app.config import settings
from app.models.problem import Problem
from app.models.coding_session import CodingSession
from app.models.message import Message


class AIService:

    def __init__(self):
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            api_key=settings.MISTRAL_API_KEY,
            temperature=0.2,
        )

    def build_system_prompt(self) -> str:
        return """
You are CodeMentor, an AI coding mentor.

You are helping a student solve a programming problem.

Your job is to:
1. Understand the problem.
2. Understand the student's current code.
3. Consider the previous conversation.
4. Answer the student's question clearly.
5. Help the student learn instead of blindly giving the answer.
6. Explain errors and suggest improvements when necessary.
7. Discuss time and space complexity when relevant.
8. Consider edge cases.
9. If the student's code is incorrect, explain why.
10. If there is a better approach, explain it.

Important:
- Do not assume code that is not provided.
- Do not invent execution results.
- If the student asks for a hint, give a hint rather than immediately giving the complete solution.
- Keep the response focused on the student's current problem and code.
"""

    def build_context(
        self,
        problem: dict,
        current_code: str,
        language: str,
    ) -> str:

        return f"""
==============================
CURRENT CODING PROBLEM
==============================

Title:
{problem.get("title", "")}

Description:
{problem.get("description", "")}

Difficulty:
{problem.get("difficulty", "")}

Constraints:
{problem.get("constraints", "")}

Examples:
{problem.get("examples", "")}


==============================
STUDENT'S CURRENT CODE
==============================

Language:
{language}

Code:

```{language}
{current_code}
==============================
END OF CURRENT CONTEXT

"""

    def chat(
        self,
        problem: dict,
        current_code: str,
        language: str,
        conversation_history: list,
        user_message: str,
    ) -> str:

        messages = []

        # 1. System instructions
        messages.append(
        SystemMessage(
            content=self.build_system_prompt()
            )
        )

        # 2. Problem + current code
        context = self.build_context(
            problem=problem,
            current_code=current_code,
            language=language,
        )

        messages.append(
        HumanMessage(
            content=context
             )
        )

        # 3. Previous conversation
        for message in conversation_history:

            role = message.get("role")
            content = message.get("content", "")

            if role == "user":
                messages.append(
                    HumanMessage(
                        content=content
                    )
                )

            elif role == "assistant":
                messages.append(
                    AIMessage(
                        content=content
                    )
                )

        # 4. Current user question
        messages.append(
            HumanMessage(
                content=user_message
            )
        )

    # 5. Call Mistral
        response = self.llm.invoke(messages)

        return response.content




    def generate_analysis_report(
    self,
    problem: Problem,
    session: CodingSession
        ) -> dict:
        """Generate a detailed analysis report of the student's code"""

        prompt = f"""You are CodeMentor, an expert code reviewer and interview coach.

            Analyze the student's solution for the following problem and return a structured report.

            ### Problem
            Title: {problem.title}
            Difficulty: {problem.difficulty.value}
            Description:
            {problem.description}

            ### Student's Code ({session.language}):
            ```{session.language}
            {session.current_code or "No code written yet"}
            Return your analysis in this exact format:
            CORRECTNESS_SCORE: <number out of 10>
            CODE_QUALITY_SCORE: <number out of 10>
            EDGE_CASE_SCORE: <number out of 10>
            TIME_COMPLEXITY: <e.g. O(n)>
            SPACE_COMPLEXITY: <e.g. O(1)>
            STRENGTHS: 
            WEAKNESSES: 
            OPTIMIZATION: 
            EXPLANATION: 
            INTERVIEW_QUESTIONS:







            """
        from langchain_core.messages import HumanMessage
        response = self.llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # Simple parser
        def extract(key: str) -> str:
            try:
                part = content.split(f"{key}:")[1].split("\n")[0].strip()
                return part
            except:
                return None
        
        def extract_block(key: str, next_keys: list) -> str:
            try:
                start = content.split(f"{key}:")[1]
                for nk in next_keys:
                    if nk in start:
                        start = start.split(nk)[0]
                return start.strip()
            except:
                return None
        
        return {
            "correctness_score": float(extract("CORRECTNESS_SCORE") or 0),
            "code_quality_score": float(extract("CODE_QUALITY_SCORE") or 0),
            "edge_case_score": float(extract("EDGE_CASE_SCORE") or 0),
            "time_complexity": extract("TIME_COMPLEXITY"),
            "space_complexity": extract("SPACE_COMPLEXITY"),
            "strengths": extract_block("STRENGTHS", ["WEAKNESSES", "OPTIMIZATION"]),
            "weaknesses": extract_block("WEAKNESSES", ["OPTIMIZATION", "EXPLANATION"]),
            "optimization_suggestions": extract_block("OPTIMIZATION", ["EXPLANATION", "INTERVIEW_QUESTIONS"]),
            "code_explanation": extract_block("EXPLANATION", ["INTERVIEW_QUESTIONS"]),
            "interview_questions": extract_block("INTERVIEW_QUESTIONS", []),
            "full_report": content
        }   








ai_service = AIService()


