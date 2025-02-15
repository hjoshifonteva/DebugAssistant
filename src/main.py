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

class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = None
    context: Optional[str] = None

class BrowserActionRequest(BaseModel):
    action: str
    url: Optional[str] = None
    browser: Optional[str] = "chrome"
    private: Optional[bool] = False
    search_terms: Optional[str] = None

class SystemCommandRequest(BaseModel):
    command: str
    params: Optional[Dict] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "gpt_client": "available",
            "memory_manager": "available",
            "code_analyzer": "available"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Debug Assistant is running",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/api/debug",
            "/api/analyze",
            "/api/browser",
            "/api/system"
        ]
    }

@app.post("/api/debug")
async def debug_code(request: DebugRequest):
    """Debug code and provide analysis"""
    try:
        print(f"Received debug request for code: {request.code[:100]}...")

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

        return {
            "analysis": {**static_analysis, **ai_analysis},
            "suggestions": fix_suggestions,
            "similar_patterns": similar_patterns,
            "browser_results": browser_results
        }

    except Exception as e:
        print(f"Error processing debug request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code without debugging context"""
    try:
        # Static code analysis
        static_analysis = code_analyzer.analyze(
            request.code,
            language=request.language
        )

        # AI-powered analysis
        ai_analysis = await gpt_client.analyze_code(
            code=request.code,
            context=request.context
        )

        return {
            "static_analysis": static_analysis,
            "ai_analysis": ai_analysis,
            "suggestions": {
                "improvements": ai_analysis.get("improvements", []),
                "best_practices": ai_analysis.get("best_practices", [])
            }
        }

    except Exception as e:
        print(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/browser")
async def execute_browser_action(request: BrowserActionRequest):
    """Execute browser-related actions"""
    try:
        result = await browser_controller.execute_action({
            "action": request.action,
            "url": request.url,
            "browser": request.browser,
            "private": request.private,
            "search_terms": request.search_terms
        })

        return {
            "status": "success",
            "action": request.action,
            "result": result
        }

    except Exception as e:
        print(f"Error executing browser action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system")
async def execute_system_command(request: SystemCommandRequest):
    """Execute system-level commands"""
    try:
        # Validate command for security
        allowed_commands = ["volume", "brightness", "app_control"]
        if request.command not in allowed_commands:
            raise HTTPException(
                status_code=400,
                detail=f"Command not allowed. Allowed commands: {allowed_commands}"
            )

        # Execute command
        result = await system_controller.execute_command(
            request.command,
            request.params or {}
        )

        return {
            "status": "success",
            "command": request.command,
            "result": result
        }

    except Exception as e:
        print(f"Error executing system command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/patterns")
async def get_debug_patterns():
    """Retrieve stored debug patterns"""
    try:
        patterns = memory_manager.find_similar_patterns()
        return {
            "patterns": patterns,
            "count": len(patterns)
        }
    except Exception as e:
        print(f"Error retrieving patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    """Get detailed system status"""
    return {
        "status": "operational",
        "components": {
            "ai_client": {
                "status": "active",
                "model": "gpt-4",
                "requests_processed": gpt_client.get_request_count()
            },
            "memory": {
                "status": "active",
                "patterns_stored": len(memory_manager.find_similar_patterns()),
                "last_updated": memory_manager.get_last_update_time()
            },
            "browser": {
                "status": "ready",
                "supported_browsers": browser_controller.get_supported_browsers()
            }
        },
        "statistics": {
            "uptime": get_uptime(),
            "requests_processed": get_request_count(),
            "memory_usage": get_memory_usage()
        }
    }

# Helper functions
def get_uptime():
    """Get server uptime"""
    # Implementation
    return "0:00:00"

def get_request_count():
    """Get total request count"""
    # Implementation
    return 0

def get_memory_usage():
    """Get current memory usage"""
    # Implementation
    return "0MB"

if __name__ == "__main__":
    print("Starting AI Debug Assistant server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)