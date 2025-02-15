import sqlite3
from typing import Dict, List, Optional
import json
from datetime import datetime


class MemoryManager:
    def __init__(self):
        self.db = sqlite3.connect('debug_memory.db')
        self.init_database()
        self.working_memory = {}
        self.last_update = datetime.now()

    def init_database(self):
        """Initialize SQLite database with enhanced schema"""
        cursor = self.db.cursor()

        # Debug sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debug_sessions (
                id INTEGER PRIMARY KEY,
                code TEXT,
                error TEXT,
                solution TEXT,
                timestamp TEXT,
                context TEXT,
                success BOOLEAN
            )
        ''')

        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                description TEXT,
                frequency INTEGER,
                last_seen TEXT
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_error ON debug_sessions(error)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON debug_sessions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern_type ON patterns(pattern_type)')

        self.db.commit()

    async def store_debug_session(self, session_data: Dict) -> bool:
        """Store debugging session data with enhanced error handling"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO debug_sessions 
                (code, error, solution, timestamp, context, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_data.get('code', ''),
                session_data.get('error', ''),
                json.dumps(session_data.get('solution', {})),
                datetime.now().isoformat(),
                session_data.get('context', ''),
                session_data.get('success', True)
            ))

            # Update pattern frequency if error exists
            if session_data.get('error'):
                self._update_pattern_frequency(session_data['error'])

            self.db.commit()
            self.last_update = datetime.now()
            return True

        except Exception as e:
            print(f"Error storing debug session: {e}")
            self.db.rollback()
            return False

    def find_similar_patterns(self, code: Optional[str] = None, error: Optional[str] = None, limit: int = 5) -> List[
        Dict]:
        """Find similar debugging patterns with enhanced matching"""
        try:
            cursor = self.db.cursor()
            query_conditions = []
            params = []

            if error:
                query_conditions.append("error LIKE ?")
                params.append(f"%{error}%")

            if code:
                query_conditions.append("code LIKE ?")
                params.append(f"%{code}%")

            query = '''
                SELECT code, error, solution, context, timestamp
                FROM debug_sessions
                '''

            if query_conditions:
                query += "WHERE " + " OR ".join(query_conditions)

            query += '''
                ORDER BY 
                    CASE WHEN success = 1 THEN 0 ELSE 1 END,
                    timestamp DESC
                LIMIT ?
            '''
            params.append(limit)

            cursor.execute(query, params)
            patterns = []

            for row in cursor.fetchall():
                try:
                    solution = json.loads(row[2])
                    patterns.append({
                        "code": row[0],
                        "error": row[1],
                        "solution": solution,
                        "context": row[3],
                        "timestamp": row[4]
                    })
                except json.JSONDecodeError:
                    continue

            return patterns

        except Exception as e:
            print(f"Error finding similar patterns: {e}")
            return []

    def _update_pattern_frequency(self, error: str):
        """Update pattern frequency in the database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO patterns 
                (pattern_type, description, frequency, last_seen)
                VALUES (
                    ?,
                    ?,
                    COALESCE((SELECT frequency + 1 FROM patterns WHERE pattern_type = ?), 1),
                    ?
                )
            ''', (error, error, error, datetime.now().isoformat()))

            self.db.commit()

        except Exception as e:
            print(f"Error updating pattern frequency: {e}")
            self.db.rollback()

    def get_last_update_time(self) -> str:
        """Get the timestamp of the last update"""
        return self.last_update.isoformat()

    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old debug sessions"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                DELETE FROM debug_sessions
                WHERE datetime(timestamp) < datetime('now', ?)
            ''', (f'-{days} days',))

            self.db.commit()

        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
            self.db.rollback()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.db.close()
        except:
            pass