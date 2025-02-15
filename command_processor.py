class CommandProcessor:
    def __init__(self):
        # Define all command keywords
        self.commands = {
            'voice_control': {
                'stop': ['stop', 'quiet', 'interrupt', 'silence', 'shut up'],
                'read': ['read', 'tell me', 'what does it say']
            },
            'screen_reading': {
                'screen': ['screen', 'display', 'window'],
                'code': ['code', 'editor', 'program']
            },
            'vscode': {
                'keywords': ['vscode', 'vs code', 'visual studio code', 'vs'],
                'actions': {
                    'open': ['open', 'launch', 'start'],
                    'create': ['create', 'make', 'new'],
                    'workspace': ['workspace', 'project', 'folder']
                }
            },
            'browser': {
                'keywords': ['chrome', 'firefox', 'browser'],
                'actions': {
                    'open': ['open', 'launch', 'start', 'go to', 'navigate'],
                    'private': ['private', 'incognito']
                }
            },
            'window': {
                'keywords': ['window', 'screen'],
                'actions': {
                    'maximize': ['maximize', 'make big', 'full screen'],
                    'minimize': ['minimize', 'make small']
                }
            }
        }

    def parse_command(self, text: str) -> dict:
        """Parse command text to identify intent and parameters"""
        text = text.lower().strip()
        words = text.split()

        # Check for voice control commands
        for action, phrases in self.commands['voice_control'].items():
            if any(phrase in text for phrase in phrases):
                if action == 'stop':
                    return {
                        "type": "voice",
                        "action": "interrupt",
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
            elif 'file' in text:
                file_path = self._extract_path(text)
                return {
                    "type": "vscode",
                    "action": "open",
                    "params": {"file": file_path}
                }
            # Default VS Code open
            return {
                "type": "vscode",
                "action": "open",
                "params": {}
            }

        # Check for browser commands
        if any(kw in text for kw in self.commands['browser']['keywords']):
            browser = self._detect_browser(text)
            url = self._extract_url(text)
            private = any(kw in text for kw in self.commands['browser']['actions']['private'])
            return {
                "type": "browser",
                "action": "open",
                "params": {
                    "browser": browser,
                    "url": url,
                    "private": private
                }
            }

        # Check for window commands
        if any(kw in text for kw in self.commands['window']['keywords']):
            action = "maximize" if any(kw in text for kw in self.commands['window']['actions']['maximize']) else "minimize"
            app = self._detect_app(text)
            return {
                "type": "window",
                "action": action,
                "params": {"app": app}
            }

        # Default to AI query for unrecognized commands
        return {
            "type": "ai_query",
            "action": "process",
            "params": {"query": text}
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
            if '.' in word and not word.startswith('.'):
                return word
        return ""

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