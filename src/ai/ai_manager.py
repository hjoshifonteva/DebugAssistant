from openai import AsyncOpenAI
import json
import os
from typing import Dict, Any


class AIManager:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """You are a programming assistant that controls VS Code and other applications.
        Always respond in JSON format with the following structure:
        {
            "command": {
                "type": "vscode|system",
                "action": "action_name",
                "params": {
                    "param1": "value1"
                }
            },
            "response": "short message to user"
        }

        Example for opening VS Code:
        {
            "command": {
                "type": "vscode",
                "action": "open",
                "params": {}
            },
            "response": "Opening VS Code"
        }

        Example for opening a file:
        {
            "command": {
                "type": "vscode",
                "action": "open_file",
                "params": {
                    "path": "path/to/file.txt"
                }
            },
            "response": "Opening specified file"
        }

        Keep responses concise and clear."""

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through OpenAI and return structured response"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=150
            )

            # Parse the response as JSON
            response_text = response.choices[0].message.content
            return json.loads(response_text)

        except json.JSONDecodeError:
            return {
                "command": {"type": "error", "action": "none", "params": {}},
                "response": "Could not parse AI response"
            }
        except Exception as e:
            return {
                "command": {"type": "error", "action": "none", "params": {}},
                "response": f"Error: {str(e)}"
            }

    async def test_connection(self) -> bool:
        """Test connection to OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": "Test connection"}
                ],
                max_tokens=50
            )
            return True
        except Exception as e:
            print(f"Failed to connect to OpenAI: {e}")
            return False