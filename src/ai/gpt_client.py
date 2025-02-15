from openai import AsyncOpenAI
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GPTClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.request_count = 0

    async def analyze_code(self, code: str, error: Optional[str] = None, context: Optional[str] = None) -> Dict:
        """Analyze code and provide debugging suggestions"""
        self.request_count += 1
        messages = [
            {"role": "system", "content": "You are an expert programming assistant specializing in debugging and code analysis."},
            {"role": "user", "content": self._create_analysis_prompt(code, error, context)}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in analyze_code: {str(e)}")
            return {
                "error": str(e),
                "analysis": {"issues": [], "root_cause": "Error analyzing code"},
                "suggestions": {"fixes": [], "improvements": [], "best_practices": []}
            }

    async def suggest_fix(self, code: str, analysis: Dict, similar_patterns: List[Dict]) -> Dict:
        """Generate fix suggestions based on analysis and similar patterns"""
        self.request_count += 1
        messages = [
            {"role": "system", "content": "You are an expert programming assistant specializing in code fixes and improvements."},
            {"role": "user", "content": self._create_fix_prompt(code, analysis, similar_patterns)}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in suggest_fix: {str(e)}")
            return {
                "error": str(e),
                "fixes": [],
                "alternatives": [],
                "implementation_steps": []
            }

    def _create_analysis_prompt(self, code: str, error: Optional[str], context: Optional[str]) -> str:
        """Create prompt for code analysis"""
        prompt = f"""
        Please analyze the following code:
        ```
        {code}
        ```

        {f'Error message:\n{error}\n' if error else ''}
        {f'Additional context:\n{context}\n' if context else ''}

        Please provide:
        1. Detailed analysis of potential issues
        2. Root cause identification
        3. Suggested improvements
        4. Best practices that could prevent similar issues

        Format your response as JSON with the following structure:
        {{
            "analysis": {{"issues": [], "root_cause": ""}},
            "suggestions": {{"fixes": [], "improvements": [], "best_practices": []}}
        }}
        """
        return prompt

    def _create_fix_prompt(self, code: str, analysis: Dict, similar_patterns: List[Dict]) -> str:
        """Create prompt for fix suggestions"""
        patterns_str = json.dumps(similar_patterns, indent=2)
        prompt = f"""
        Given this code:
        ```
        {code}
        ```

        Analysis results:
        {json.dumps(analysis, indent=2)}

        Similar patterns found:
        {patterns_str}

        Please provide:
        1. Specific code fixes
        2. Alternative solutions
        3. Implementation guidance

        Format your response as JSON with the following structure:
        {{
            "fixes": [
                {{"description": "", "code": "", "explanation": ""}}
            ],
            "alternatives": [
                {{"approach": "", "benefits": [], "code_example": ""}}
            ],
            "implementation_steps": []
        }}
        """
        return prompt

    def _parse_response(self, response: str) -> Dict:
        """Parse GPT response and ensure it's valid JSON"""
        try:
            # Extract JSON from response if it's wrapped in markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse response",
                "raw_response": response
            }

    def get_request_count(self) -> int:
        """Get the total number of requests made"""
        return self.request_count