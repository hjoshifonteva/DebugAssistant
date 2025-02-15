import sqlite3
from typing import Dict, List, Optional
import json
from datetime import datetime


class MemoryManager:
    def __init__(self):
        self.db = sqlite3.connect('debug_memory.db')
        self.init_database()
        self.working_memory = {}

    def init_database(self):
        """Initialize SQLite database"""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debug_sessions (
                id INTEGER PRIMARY KEY,
                code TEXT,
                error TEXT,
                solution TEXT,
                timestamp TEXT,
                context TEXT
            )
        ''')
        self.db.commit()

    async def store_debug_session(self, session_data: Dict):
        """Store debugging session data"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO debug_sessions (code, error, solution, timestamp, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_data.get('code', ''),
                session_data.get('error', ''),
                json.dumps(session_data.get('solution', {})),
                datetime.now().isoformat(),
                session_data.get('context', '')
            ))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error storing debug session: {e}")
            return False

    def find_similar_patterns(self, code: str, error: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Find similar debugging patterns"""
        try:
            cursor = self.db.cursor()
            if error:
                cursor.execute('''
                    SELECT code, error, solution, context
                    FROM debug_sessions
                    WHERE error LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f"%{error}%", limit))
            else:
                cursor.execute('''
                    SELECT code, error, solution, context
                    FROM debug_sessions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

            patterns = []
            for row in cursor.fetchall():
                try:
                    solution = json.loads(row[2])
                    patterns.append({
                        "code": row[0],
                        "error": row[1],
                        "solution": solution,
                        "context": row[3]
                    })
                except json.JSONDecodeError:
                    continue

            return patterns
        except Exception as e:
            print(f"Error finding similar patterns: {e}")
            return []