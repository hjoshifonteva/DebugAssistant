import os
import sys
import asyncio
import speech_recognition as sr
import threading
import queue
import subprocess
import time
import requests
from dotenv import load_dotenv

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Now import our modules
from src.voice_manager import VoiceManager
from src.utils.screen_reader import ScreenReader
from src.system_controller import SystemController
from command_processor import CommandProcessor
from src.ai.ai_manager import AIManager

# Load environment variables
load_dotenv()


class ServerManager:
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.server_process = None

    def start_server(self):
        """Start the FastAPI server"""
        try:
            server_script = os.path.join("src", "main.py")
            self.server_process = subprocess.Popen([sys.executable, server_script])

            # Wait for server to start
            for _ in range(5):
                try:
                    response = requests.get(f"{self.server_url}/")
                    if response.status_code == 200:
                        print("Debug server started successfully!")
                        return True
                except requests.exceptions.ConnectionError:
                    time.sleep(2)
            return False
        except Exception as e:
            print(f"Error starting server: {e}")
            return False

    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            self.server_process.terminate()
            print("Server stopped")


class DebugAssistantClient:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.running = False
        self.server_manager = ServerManager()
        self.system_controller = SystemController()
        self.command_processor = CommandProcessor()
        self.ai_manager = AIManager()
        self.voice_manager = VoiceManager()
        self.screen_reader = ScreenReader()

    async def start(self):
        """Start all services"""
        self.voice_manager.speak("Starting Debug Assistant...")

        # Start server
        if not self.server_manager.start_server():
            self.voice_manager.speak("Failed to start debug server")
            return False

        # Test OpenAI connection
        if not await self.ai_manager.test_connection():
            self.voice_manager.speak("Warning: OpenAI connection failed. Please check your API key.")
            return False

        return True

    async def process_command(self, command_type: str, command: str):
        """Process command"""
        try:
            if command.lower() == 'quit':
                self.running = False
                self.voice_manager.speak("Shutting down...")
                return

            if command.lower() == 'help':
                self.show_help()
                return

            # Parse command
            parsed = self.command_processor.parse_command(command)

            # Handle voice control
            if parsed['type'] == 'voice':
                if parsed['action'] == 'interrupt':
                    self.voice_manager.interrupt_speech()
                    return

            # Handle screen reading
            if parsed['type'] == 'screen':
                if parsed['action'] == 'read':
                    text = self.screen_reader.read_text_from_image(
                        self.screen_reader.capture_window(None)
                    )
                    self.voice_manager.speak(f"I see this text: {text}")
                    return
                elif parsed['action'] == 'read_code':
                    code = self.screen_reader.read_code_from_editor()
                    self.voice_manager.speak(f"I see this code: {code}")
                    await self.ai_manager.analyze_code(code)
                    return

            # Handle VS Code commands
            if parsed['type'] == "vscode":
                result = self.system_controller.execute_command({
                    "type": "vscode",
                    "action": parsed["action"],
                    "params": parsed["params"]
                })
                self.voice_manager.speak(result["message"])
                return

            # Handle browser commands
            if parsed['type'] == "browser":
                result = self.system_controller.execute_command({
                    "type": "browser",
                    "action": parsed["action"],
                    "params": parsed["params"]
                })
                self.voice_manager.speak(result["message"])
                return

            # Handle window commands
            if parsed['type'] == "window":
                result = self.system_controller.execute_command({
                    "type": "window",
                    "action": parsed["action"],
                    "params": parsed["params"]
                })
                self.voice_manager.speak(result["message"])
                return

            # Default to AI query
            await self.ai_manager.process_query(command)

        except Exception as e:
            self.voice_manager.speak(f"Error: {str(e)}")
            print(f"Error processing command: {e}")
            self.show_help()

    def show_help(self):
        help_text = """
        Available Commands:
        1. Voice Control:
           - 'stop talking' - Interrupt current speech
           - 'read screen' - Read text from screen
           - 'read code' - Read and analyze code from editor

        2. VS Code Control:
           - 'open vs code'
           - 'create workspace python_project'
           - 'open file example.py'

        3. Browser Control:
           - 'open chrome'
           - 'open firefox in private mode'
           - 'go to github.com'

        4. Window Management:
           - 'maximize vs code'
           - 'minimize chrome'
           - 'maximize all windows'

        5. General:
           - Ask anything! AI will help
           - 'help' - Show this help
           - 'quit' - Exit
        """
        print(help_text)
        self.voice_manager.speak(
            "I can help with VS Code, read text and code, control browsers, and more. What would you like to do?")

    def voice_listener(self):
        """Listen for voice commands"""
        recognizer = sr.Recognizer()

        while self.running:
            try:
                with sr.Microphone() as source:
                    print("\nListening...")
                    audio = recognizer.listen(source)

                try:
                    command = recognizer.recognize_google(audio)
                    print(f"\n🎙️ You said: {command}")
                    self.command_queue.put(("voice", command))
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
            except Exception as e:
                print(f"Error in voice listening: {e}")

    def chat_listener(self):
        """Listen for chat input"""
        while self.running:
            try:
                user_input = input("\nEnter command (or 'quit' to exit): ")
                self.command_queue.put(("chat", user_input))
            except Exception as e:
                print(f"Error in chat input: {e}")

    async def run(self):
        """Run the assistant"""
        if not await self.start():
            return

        self.running = True

        voice_thread = threading.Thread(target=self.voice_listener)
        chat_thread = threading.Thread(target=self.chat_listener)

        voice_thread.daemon = True
        chat_thread.daemon = True

        voice_thread.start()
        chat_thread.start()

        self.voice_manager.speak("Debug Assistant is ready! How can I help?")
        self.show_help()

        try:
            while self.running:
                try:
                    command_type, command = self.command_queue.get(timeout=1)
                    await self.process_command(command_type, command)
                except queue.Empty:
                    continue
        except KeyboardInterrupt:
            self.voice_manager.speak("Shutting down...")
        finally:
            self.running = False
            self.voice_manager.shutdown()
            self.server_manager.stop_server()


if __name__ == "__main__":
    assistant = DebugAssistantClient()
    asyncio.run(assistant.run())