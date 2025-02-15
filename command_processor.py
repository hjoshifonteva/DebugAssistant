from typing import Dict, Any, List


class EnhancedCommandProcessor:
    def __init__(self):
        # Define all command keywords
        self.commands = {
            'voice_control': {
                'stop': ['stop', 'quiet', 'interrupt', 'silence', 'shut up', 'be quiet',
                         'stop talking', 'pause', 'hold on', 'wait'],
                'resume': ['continue', 'resume', 'go on', 'keep talking'],
                'read': ['read', 'tell me', 'what does it say', 'read this',
                         'analyze this', 'explain this']
            },
            'screen_reading': {
                'screen': ['screen', 'display', 'window', 'show me'],
                'code': ['code', 'editor', 'program', 'script', 'function']
            },
            'vscode': {
                'keywords': ['vscode', 'vs code', 'visual studio code', 'vs', 'editor'],
                'actions': {
                    'open': ['open', 'launch', 'start', 'run'],
                    'create': ['create', 'make', 'new', 'generate'],
                    'workspace': ['workspace', 'project', 'folder', 'directory'],
                    'save': ['save', 'store', 'write'],
                    'close': ['close', 'exit', 'quit']
                }
            },
            'browser': {
                'keywords': ['chrome', 'firefox', 'browser', 'web', 'internet'],
                'actions': {
                    'open': ['open', 'launch', 'start', 'go to', 'navigate', 'browse'],
                    'private': ['private', 'incognito', 'secret'],
                    'search': ['search', 'find', 'look up', 'google'],
                    'close': ['close', 'exit', 'quit', 'stop']
                }
            },
            'window': {
                'keywords': ['window', 'screen', 'application', 'app'],
                'actions': {
                    'maximize': ['maximize', 'make big', 'full screen', 'enlarge'],
                    'minimize': ['minimize', 'make small', 'hide'],
                    'restore': ['restore', 'normal size', 'reset size'],
                    'switch': ['switch to', 'change to', 'go to']
                }
            },
            'system': {
                'keywords': ['system', 'computer', 'pc'],
                'actions': {
                    'volume': ['volume', 'sound', 'audio'],
                    'brightness': ['brightness', 'screen light'],
                    'shutdown': ['shutdown', 'turn off', 'power off'],
                    'restart': ['restart', 'reboot', 'reload']
                }
            }
        }

    def parse_command(self, text: str) -> dict:
        """Parse command text to identify intent and parameters"""
        text = text.lower().strip()

        # Check for voice control commands first (highest priority)
        for action, phrases in self.commands['voice_control'].items():
            if self._fuzzy_match_phrases(text, phrases):
                return {
                    "type": "voice",
                    "action": action,
                    "params": {}
                }

        # Check for screen reading commands
        if any(word in text for word in self.commands['screen_reading']['screen']):
            if any(word in text for word in self.commands['screen_reading']['code']):
                return {
                    "type": "screen",
                    "action": "read_code",
                    "params": {}
                }
            return {
                "type": "screen",
                "action": "read",
                "params": {}
            }

        # Check for VS Code commands
        if any(kw in text for kw in self.commands['vscode']['keywords']):
            return self._parse_vscode_command(text)

        # Check for browser commands
        if any(kw in text for kw in self.commands['browser']['keywords']):
            return self._parse_browser_command(text)

        # Check for window commands
        if any(kw in text for kw in self.commands['window']['keywords']):
            return self._parse_window_command(text)

        # Check for system commands
        if any(kw in text for kw in self.commands['system']['keywords']):
            return self._parse_system_command(text)

        # Default to AI query for unrecognized commands
        return {
            "type": "ai_query",
            "action": "process",
            "params": {"query": text}
        }

    def _fuzzy_match_phrases(self, text: str, phrases: List[str]) -> bool:
        """Improved fuzzy matching for commands"""
        for phrase in phrases:
            if phrase in text:
                return True
            # Check for partial matches
            words = phrase.split()
            if len(words) > 1:
                matched_words = sum(1 for word in words if word in text.split())
                if matched_words / len(words) >= 0.7:  # 70% match threshold
                    return True
        return False

    def _parse_vscode_command(self, text: str) -> Dict[str, Any]:
        """Parse VS Code specific commands"""
        if any(kw in text for kw in self.commands['vscode']['actions']['create']):
            # Handle workspace creation
            if any(kw in text for kw in self.commands['vscode']['actions']['workspace']):
                name = self._extract_name(text)
                return {
                    "type": "vscode",
                    "action": "create_workspace",
                    "params": {"name": name or "new_workspace"}
                }

        # Handle file opening
        if 'file' in text:
            file_path = self._extract_path(text)
            return {
                "type": "vscode",
                "action": "open_file",
                "params": {"file": file_path}
            }

        # Default VS Code open
        return {
            "type": "vscode",
            "action": "open",
            "params": {}
        }

    def _parse_browser_command(self, text: str) -> Dict[str, Any]:
        """Parse browser specific commands"""
        browser = self._detect_browser(text)
        url = self._extract_url(text)
        private = any(kw in text for kw in self.commands['browser']['actions']['private'])

        # Check for search command
        if any(kw in text for kw in self.commands['browser']['actions']['search']):
            search_terms = self._extract_search_terms(text)
            return {
                "type": "browser",
                "action": "search",
                "params": {
                    "browser": browser,
                    "terms": search_terms,
                    "private": private
                }
            }

        # Handle URL navigation
        if url:
            return {
                "type": "browser",
                "action": "open",
                "params": {
                    "browser": browser,
                    "url": url,
                    "private": private
                }
            }

        # Default browser open
        return {
            "type": "browser",
            "action": "open",
            "params": {
                "browser": browser,
                "private": private
            }
        }

    def _parse_window_command(self, text: str) -> Dict[str, Any]:
        """Parse window management commands"""
        for action, keywords in self.commands['window']['actions'].items():
            if any(kw in text for kw in keywords):
                app = self._detect_app(text)
                return {
                    "type": "window",
                    "action": action,
                    "params": {"app": app}
                }
        return {
            "type": "window",
            "action": "focus",
            "params": {"app": self._detect_app(text)}
        }

    def _parse_system_command(self, text: str) -> Dict[str, Any]:
        """Parse system control commands"""
        for action, keywords in self.commands['system']['actions'].items():
            if any(kw in text for kw in keywords):
                if action == 'volume':
                    level = self._extract_number(text)
                    return {
                        "type": "system",
                        "action": "set_volume",
                        "params": {"level": level if level is not None else 50}
                    }
                if action == 'brightness':
                    level = self._extract_number(text)
                    return {
                        "type": "system",
                        "action": "set_brightness",
                        "params": {"level": level if level is not None else 50}
                    }
                return {
                    "type": "system",
                    "action": action,
                    "params": {}
                }
        return {
            "type": "system",
            "action": "unknown",
            "params": {}
        }

    def _extract_name(self, text: str) -> str:
        """Extract project/workspace name from command"""
        keywords = ['called', 'named', 'name', 'workspace', 'project']
        words = text.split()
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                return words[i + 1]
        return ""

    def _extract_path(self, text: str) -> str:
        """Extract file path from command"""
        words = text.split()
        if 'file' in words:
            idx = words.index('file')
            if idx + 1 < len(words):
                return words[idx + 1]
        return ""

    def _extract_url(self, text: str) -> str:
        """Extract URL from command"""
        words = text.split()
        for word in words:
            if ('.' in word and
                    not word.startswith('.') and
                    not word.endswith('.') and
                    ' ' not in word):
                return word
        return ""

    def _extract_search_terms(self, text: str) -> str:
        """Extract search terms from command"""
        search_keywords = ['search', 'find', 'look up', 'google']
        for keyword in search_keywords:
            if keyword in text:
                parts = text.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return ""

    def _extract_number(self, text: str) -> int:
        """Extract number from command"""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None

    def _detect_browser(self, text: str) -> str:
        """Detect which browser is mentioned"""
        if 'chrome' in text:
            return 'chrome'
        elif 'firefox' in text:
            return 'firefox'
        return 'chrome'  # default

    def _detect_app(self, text: str) -> str:
        """Detect which app is mentioned"""
        apps = ['vscode', 'chrome', 'firefox', 'notepad']
        for app in apps:
            if app in text:
                return app
        return "active"  # default to active window