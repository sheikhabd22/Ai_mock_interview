"""LLM-based evaluation engine for interview answers."""
import os
import json
import re
from typing import List, Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            print("GROQ API key not found")
            self.client = None
            self.is_llm_configured = False
            return

        self.client = OpenAI(api_key=self.api_key,base_url="https://api.groq.com/openai/v1")
        self.model_name = "llama-3.1-8b-instant"
        self.is_llm_configured = True

    def generate_questions(self, role: str, experience_level: str,
                       interview_type: str, num_questions: int = 5,
                       resume_text: str = None) -> List[str]:

        if not self.is_llm_configured or self.client is None:
            return self._get_fallback_questions(role, interview_type, num_questions)

        prompt = f"""You are an expert interviewer. Generate exactly {num_questions} interview questions for:

        - Job Role: {role}
        - Experience Level: {experience_level}
        - Interview Type: {interview_type}

        Return each question on a new line.
        Do NOT number them.
        Do NOT add explanations.
            """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                        {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()

            questions = content.split("\n")
            questions = [q.strip() for q in questions if q.strip()]

            return questions[:num_questions]

        except Exception as e:
            print(f"LLM Error generating questions: {e}")
            return self._get_fallback_questions(role, interview_type, num_questions)

    def evaluate_answer(self, question: str, answer: str, role: str,
                        experience_level: str) -> Dict[str, Any]:
        """Evaluate an interview answer using the LLM."""
        if not self.is_llm_configured or self.client is None:
            return self._get_fallback_evaluation()

        prompt = f"""You are an expert interview evaluator. Evaluate the following interview answer.

Job Role: {role}
Experience Level: {experience_level}

Question: {question}

Candidate's Answer: {answer}

Evaluate the answer on these criteria (score each 0-10):
1. Technical Accuracy - How technically correct is the answer?
2. Clarity - How clear and well-structured is the explanation?
3. Completeness - Does the answer cover all important points?
4. Communication - How well does the candidate communicate?

Provide your evaluation as a JSON object with this EXACT structure:
{{
    "overall_score": <float 0-10>,
    "technical_accuracy": <float 0-10>,
    "clarity": <float 0-10>,
    "completeness": <float 0-10>,
    "communication": <float 0-10>,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
}}

Return ONLY the JSON object, no other text.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            content = response.choices[0].message.content.strip()

            # Extract JSON object from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return self._validate_evaluation(result)

            return json.loads(content)

        except Exception as e:
            print(f"LLM Error evaluating answer: {e}")
            return self._get_fallback_evaluation()

    def generate_final_report_summary(self, answers: list, role: str) -> Dict[str, List[str]]:
        """Generate a summary of strengths, weaknesses, and suggestions for the full interview."""
        if not self.is_llm_configured or self.client is None:
            return {
                "strengths": ["Completed the interview"],
                "weaknesses": ["Detailed AI summary unavailable without configured LLM"],
                "suggestions": ["Configure MODEL_NAME and BASE_URL in .env for richer summaries"],
            }

        answers_text = ""
        for i, ans in enumerate(answers, 1):
            answers_text += f"\nQ{i}: {ans.get('question', 'N/A')}\nScore: {ans.get('evaluation_score', 'N/A')}/10\n"

        prompt = f"""Based on the following interview performance for the role of {role}, provide an overall summary.

{answers_text}

Return a JSON object with:
{{
    "strengths": ["overall strength 1", "overall strength 2", "overall strength 3"],
    "weaknesses": ["overall weakness 1", "overall weakness 2"],
    "suggestions": ["actionable suggestion 1", "actionable suggestion 2", "actionable suggestion 3"]
}}

Return ONLY the JSON object.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert interview coach. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
            )
            content = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except Exception:
            return {
                "strengths": ["Completed the interview"],
                "weaknesses": ["Review individual question feedback"],
                "suggestions": ["Practice more with mock interviews"]
            }

    def _validate_evaluation(self, result: Dict) -> Dict:
        """Ensure evaluation result has all required fields with valid values."""
        defaults = {
            "overall_score": 5.0,
            "technical_accuracy": 5.0,
            "clarity": 5.0,
            "completeness": 5.0,
            "communication": 5.0,
            "strengths": ["Answer provided"],
            "weaknesses": ["Could be improved"],
            "suggestions": ["Practice more"]
        }
        for key, default in defaults.items():
            if key not in result:
                result[key] = default
            elif isinstance(default, float):
                try:
                    result[key] = min(10.0, max(0.0, float(result[key])))
                except (ValueError, TypeError):
                    result[key] = default
        return result

    def _get_fallback_evaluation(self) -> Dict:
        """Return a fallback evaluation when LLM is unavailable."""
        return {
            "overall_score": 5.0,
            "technical_accuracy": 5.0,
            "clarity": 5.0,
            "completeness": 5.0,
            "communication": 5.0,
            "strengths": ["Answer was provided"],
            "weaknesses": ["Could not perform AI evaluation - using defaults"],
            "suggestions": ["Ensure LLM service is running for detailed feedback"]
        }

    def _get_fallback_questions(self, role: str, interview_type: str, num: int) -> List[str]:
        """Return fallback questions when LLM is unavailable."""
        technical = [
            f"Explain the key technical skills required for a {role} position.",
            f"Describe a challenging technical problem you solved as a {role}.",
            f"What tools and technologies do you use in your role as a {role}?",
            f"How do you approach debugging and troubleshooting in your work?",
            f"Explain a concept that is fundamental to the {role} position.",
        ]
        hr = [
            "Tell me about yourself and your professional journey.",
            "Describe a situation where you had to work with a difficult team member.",
            "What are your greatest strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Why are you interested in this position?",
        ]
        if interview_type.lower() == "technical":
            return technical[:num]
        elif interview_type.lower() == "hr":
            return hr[:num]
        else:
            mixed = technical[:3] + hr[:2]
            return mixed[:num]


# Singleton instance
llm_engine = LLMEngine()
