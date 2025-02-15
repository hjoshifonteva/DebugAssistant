from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai.gpt_client import GPTClient
from src.memory.manager import MemoryManager
from src.analysis.code_analyzer import CodeAnalyzer
from src.automation.browser_controller import BrowserController

app = FastAPI(title="AI Debug Assistant")
gpt_client = GPTClient()
memory_manager = MemoryManager()
code_analyzer = CodeAnalyzer()
browser_controller = BrowserController()


class DebugRequest(BaseModel):
    code: str
    error: Optional[str] = None
    context: Optional[str] = None
    browser_actions: Optional[List[Dict]] = None


class DebugResponse(BaseModel):
    analysis: Dict
    suggestions: Dict
    similar_patterns: Optional[List[Dict]]
    browser_results: Optional[Dict]


@app.get("/")
async def root():
    return {"message": "AI Debug Assistant is running"}


@app.get("/test")
async def test():
    return {"message": "Test endpoint working"}


@app.post("/api/debug")  # Changed from /debug to /api/debug
async def debug_code(request: DebugRequest):
    try:
        print(f"Received debug request for code: {request.code[:100]}...")  # Debug print

        # Initial code analysis
        static_analysis = code_analyzer.analyze(request.code)

        # Check memory for similar patterns
        similar_patterns = memory_manager.find_similar_patterns(
            code=request.code,
            error=request.error
        )

        # Get AI analysis
        ai_analysis = await gpt_client.analyze_code(
            code=request.code,
            error=request.error,
            context=request.context
        )

        # Generate fix suggestions
        fix_suggestions = await gpt_client.suggest_fix(
            code=request.code,
            analysis={**static_analysis, **ai_analysis},
            similar_patterns=similar_patterns
        )

        # Handle browser automation if requested
        browser_results = None
        if request.browser_actions:
            browser_results = await browser_controller.execute_actions(
                request.browser_actions
            )

        # Store debug session in memory
        await memory_manager.store_debug_session({
            'code': request.code,
            'error': request.error,
            'analysis': ai_analysis,
            'solution': fix_suggestions,
            'success': True
        })

        return DebugResponse(
            analysis={**static_analysis, **ai_analysis},
            suggestions=fix_suggestions,
            similar_patterns=similar_patterns,
            browser_results=browser_results
        )

    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting AI Debug Assistant server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)