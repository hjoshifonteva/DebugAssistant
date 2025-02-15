from typing import Dict, List, Optional


class PromptTemplates:
    @staticmethod
    def code_analysis(code: str, error: Optional[str] = None, context: Optional[str] = None) -> str:
        return f"""
        Please analyze this code and provide a detailed review:

        ```
        {code}
        ```
        {f'Error encountered:\n{error}\n' if error else ''}
        {f'Context:\n{context}\n' if context else ''}

        Provide the following:
        1. Potential issues and bugs
        2. Root cause analysis
        3. Code quality assessment
        4. Performance implications
        5. Security considerations

        Format as JSON:
        {{
            "issues": [
                {{"type": "", "description": "", "severity": "", "line_number": ""}}
            ],
            "root_cause": {{"description": "", "explanation": ""}},
            "quality": {{"score": 0-10, "feedback": []}},
            "performance": {{"concerns": [], "suggestions": []}},
            "security": {{"vulnerabilities": [], "recommendations": []}}
        }}
        """

    @staticmethod
    def fix_suggestion(code: str, analysis: Dict, similar_patterns: List[Dict]) -> str:
        patterns_str = "\n".join(
            [f"- {p.get('description', '')}" for p in similar_patterns]) if similar_patterns else "None found"

        return f"""
        Given this code:
        ```
        {code}
        ```

        Analysis results:
        {analysis}

        Similar patterns found:
        {patterns_str}

        Please provide:
        1. Specific code fixes
        2. Alternative approaches
        3. Step-by-step implementation guide
        4. Best practices to prevent similar issues

        Format as JSON:
        {{
            "fixes": [
                {{"code": "", "explanation": "", "impact": ""}}
            ],
            "alternatives": [
                {{"approach": "", "benefits": [], "code_example": ""}}
            ],
            "implementation": {{"steps": [], "considerations": []}},
            "prevention": {{"best_practices": [], "code_examples": []}}
        }}
        """