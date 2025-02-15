import subprocess
import os
import json
import winreg
from typing import Dict, Any, List, Optional


class SystemController:
    def __init__(self):
        # Default commands for apps
        self.default_commands = {
            "vscode": "code",
            "chrome": "chrome",
            "firefox": "firefox",
            "explorer": "explorer",
            "terminal": "wt"
        }

        # Initialize paths
        self.app_paths = {
            "vscode": {
                "path": self._find_vscode_path(),
                "command": "code",
                "args": {
                    "new_window": "--new-window",
                    "folder": "--folder-uri",
                    "goto": "--goto"
                }
            },
            "chrome": {
                "path": self._find_chrome_path(),
                "command": "chrome",
                "args": {"incognito": "--incognito"}
            },
            "firefox": {
                "path": self._find_firefox_path(),
                "command": "firefox",
                "args": {"private": "-private"}
            }
        }

        self.workspace_root = os.path.expanduser("~/workspace")
        self._ensure_directories()

    def _find_vscode_path(self) -> str:
        """Find VS Code installation path"""
        possible_paths = [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        ]

        # Try registry first
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Code.exe")
            path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(path):
                return path
        except:
            pass

        # Try possible paths
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                return expanded_path

        return self.default_commands["vscode"]

    def _find_chrome_path(self) -> str:
        """Find Chrome installation path"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(path):
                return path
        except:
            pass
        return self.default_commands["chrome"]

    def _find_firefox_path(self) -> str:
        """Find Firefox installation path"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe")
            path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(path):
                return path
        except:
            pass
        return self.default_commands["firefox"]

    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.workspace_root, exist_ok=True)

    def execute_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system commands based on command type"""
        try:
            cmd_type = command_data.get("type", "")
            action = command_data.get("action", "")
            params = command_data.get("params", {})

            if cmd_type == "vscode":
                return self._handle_vscode_command(action, params)
            elif cmd_type == "system":
                return self._handle_system_command(action, params)
            else:
                return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_vscode_command(self, action: str, params: Dict) -> Dict[str, Any]:
        """Handle VS Code specific commands"""
        try:
            if action == "open":
                # Open VS Code with specified file or folder
                file_path = params.get("path", "")
                if file_path:
                    subprocess.Popen([self.app_paths["vscode"]["path"], file_path])
                    return {"status": "success", "message": f"Opened {file_path} in VS Code"}
                else:
                    subprocess.Popen([self.app_paths["vscode"]["path"]])
                    return {"status": "success", "message": "Opened VS Code"}

            elif action == "open_file":
                file_path = params.get("path", "")
                if not file_path:
                    return {"status": "error", "message": "No file path provided"}
                subprocess.Popen([self.app_paths["vscode"]["path"], "--goto", file_path])
                return {"status": "success", "message": f"Opened file: {file_path}"}

            return {"status": "error", "message": f"Unknown VS Code action: {action}"}

        except Exception as e:
            return {"status": "error", "message": f"VS Code error: {str(e)}"}

    def _handle_system_command(self, action: str, params: Dict) -> Dict[str, Any]:
        """Handle general system commands"""
        try:
            if action == "open_app":
                app_name = params.get("app", "").lower()
                if app_name in self.app_paths:
                    subprocess.Popen([self.app_paths[app_name]["path"]])
                    return {"status": "success", "message": f"Opened {app_name}"}
                return {"status": "error", "message": f"Unknown application: {app_name}"}

            return {"status": "error", "message": f"Unknown system action: {action}"}

        except Exception as e:
            return {"status": "error", "message": f"System error: {str(e)}"}