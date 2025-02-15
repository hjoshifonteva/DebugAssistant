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
from src.voice_manager import EnhancedVoiceManager
from src.utils.screen_reader import ScreenReader
from src.system_controller import SystemController
from command_processor import EnhancedCommandProcessor
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
            if not os.path.exists(server_script):
                print(f"Error: Server script not found at {server_script}")
                return False

            self.server_process = subprocess.Popen([sys.executable, server_script])
            print("Starting server process...")

            # Wait for server to start
            max_retries = 5
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    response = requests.get(f"{self.server_url}/health")
                    if response.status_code == 200:
                        print("Debug server started successfully!")
                        return True
                except requests.exceptions.ConnectionError:
                    print(f"Waiting for server to start (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)

            print("Server failed to start after maximum retries")
            return False
        except Exception as e:
            print(f"Error starting server: {e}")
            return False

    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("Server stopped successfully")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("Server forcefully terminated")
            except Exception as e:
                print(f"Error stopping server: {e}")
            finally:
                self.server_process = None


class DebugAssistantClient:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.running = False
        self.server_manager = ServerManager()
        self.system_controller = SystemController()
        self.command_processor = EnhancedCommandProcessor()
        self.ai_manager = AIManager()
        self.voice_manager = EnhancedVoiceManager()
        self.screen_reader = ScreenReader()
        self.recognition_threshold = 0.7  # Confidence threshold for speech recognition
        self.last_command = None
        self.command_history = []
        self.max_history = 10

    async def start(self):
        """Start all services"""
        print("\n=== Starting AI Debug Assistant ===")
        self.voice_manager.speak("Initializing Debug Assistant...")

        # Start server
        if not self.server_manager.start_server():
            self.voice_manager.speak("Warning: Failed to start debug server")
            return False

        # Test OpenAI connection
        if not await self.ai_manager.test_connection():
            self.voice_manager.speak("Warning: OpenAI connection failed. Please check your API key.")
            return False

        # Initialize screen reader
        try:
            capture = self.screen_reader.capture_window(None)
            if capture:
                print("Screen reader initialized successfully")
        except Exception as e:
            print(f"Warning: Screen reader initialization error: {e}")

        # Test text-to-speech
        self.voice_manager.speak("System initialization complete!")
        return True

    def add_to_history(self, command: str):
        """Add command to history"""
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

    async def process_command(self, command_type: str, command: str):
        """Process command with enhanced error handling and features"""
        try:
            # Add to history
            self.add_to_history(command)
            self.last_command = command

            # Handle system commands
            if command.lower() == 'quit':
                self.running = False
                self.voice_manager.speak("Shutting down. Goodbye!")
                return

            if command.lower() == 'help':
                self.show_help()
                return

            if command.lower() == 'history':
                self.show_command_history()
                return

            if command.lower() == 'repeat':
                if self.last_command:
                    await self.process_command(command_type, self.last_command)
                return

            # Parse and process command
            parsed = self.command_processor.parse_command(command)

            # Handle voice control
            if parsed['type'] == 'voice':
                await self._handle_voice_command(parsed)
                return

            # Handle screen reading
            if parsed['type'] == 'screen':
                await self._handle_screen_command(parsed)
                return

            # Handle VS Code
            if parsed['type'] == "vscode":
                await self._handle_vscode_command(parsed)
                return

            # Handle browser
            if parsed['type'] == "browser":
                await self._handle_browser_command(parsed)
                return

            # Handle window
            if parsed['type'] == "window":
                await self._handle_window_command(parsed)
                return

            # Handle system
            if parsed['type'] == "system":
                await self._handle_system_command(parsed)
                return

            # Default to AI query
            response = await self.ai_manager.process_query(command)
            self.voice_manager.speak(response.get("response", ""))

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(error_msg)
            self.voice_manager.speak(f"Sorry, I encountered an error: {str(e)}")

    async def _handle_voice_command(self, parsed):
        """Handle voice control commands"""
        if parsed['action'] == 'stop':
            self.voice_manager.interrupt_speech()
        elif parsed['action'] == 'resume':
            self.voice_manager.resume_speech()
        elif parsed['action'] == 'volume':
            level = parsed['params'].get('level', 50)
            if 'up' in parsed['params'].get('direction', ''):
                self.voice_manager.increase_volume()
            else:
                self.voice_manager.decrease_volume()

    async def _handle_screen_command(self, parsed):
        """Handle screen reading commands"""
        if parsed['action'] == 'read':
            image = self.screen_reader.capture_window(None)
            if image:
                text = self.screen_reader.read_text_from_image(image)
                self.voice_manager.speak(f"I see this text: {text}")
        elif parsed['action'] == 'read_code':
            code = self.screen_reader.read_code_from_editor()
            if code:
                self.voice_manager.speak("I found this code. Analyzing...")
                analysis = await self.ai_manager.analyze_code(code)
                self.voice_manager.speak(str(analysis))

    async def _handle_vscode_command(self, parsed):
        """Handle VS Code commands"""
        result = self.system_controller.execute_command(parsed)
        self.voice_manager.speak(result["message"])

    async def _handle_browser_command(self, parsed):
        """Handle browser commands"""
        result = self.system_controller.execute_command(parsed)
        self.voice_manager.speak(result["message"])

    async def _handle_window_command(self, parsed):
        """Handle window management commands"""
        result = self.system_controller.execute_command(parsed)
        self.voice_manager.speak(result["message"])

    async def _handle_system_command(self, parsed):
        """Handle system control commands"""
        result = self.system_controller.execute_command(parsed)
        self.voice_manager.speak(result["message"])

    def show_command_history(self):
        """Display command history"""
        if not self.command_history:
            self.voice_manager.speak("No commands in history")
            return

        print("\nCommand History:")
        for i, cmd in enumerate(self.command_history, 1):
            print(f"{i}. {cmd}")

        self.voice_manager.speak("Showing command history on screen")

    def show_help(self):
        """Display help information"""
        help_text = """
        === AI Debug Assistant Commands ===

        1. Voice Control:
           - 'stop talking' or Ctrl+Shift+Space - Interrupt speech
           - 'continue' or Ctrl+Shift+R - Resume speech
           - Ctrl+Shift+Up/Down - Adjust volume
           - Ctrl+Shift+Left/Right - Adjust speech rate

        2. Screen Reading:
           - 'read screen' - Read text from screen
           - 'read code' - Read and analyze code
           - 'show me' - Display current screen
           - 'analyze this' - Analyze visible code

        3. VS Code Control:
           - 'open vs code'
           - 'create workspace <name>'
           - 'open file <path>'
           - 'save file'
           - 'close vs code'

        4. Browser Control:
           - 'open chrome/firefox'
           - 'search for <query>'
           - 'go to <website>'
           - 'open private window'
           - 'close browser'

        5. Window Management:
           - 'maximize/minimize <app>'
           - 'restore window'
           - 'switch to <app>'

        6. System Control:
           - 'set volume <level>'
           - 'adjust brightness'
           - 'restart system'
           - 'shutdown computer'

        7. Utility Commands:
           - 'help' - Show this help
           - 'history' - Show command history
           - 'repeat' - Repeat last command
           - 'quit' - Exit assistant

        Note: You can also ask me any questions about coding, debugging, or system operations!
        """
        print(help_text)
        self.voice_manager.speak(
            "I've displayed the help menu on screen. I can help with voice control, screen reading, "
            "VS Code, browsers, system control and more. What would you like to do?"
        )

    def voice_listener(self):
        """Enhanced voice command listener"""
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 4000

        while self.running:
            try:
                with sr.Microphone() as source:
                    print("\nListening...")
                    # Reduce ambient noise impact
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    command = recognizer.recognize_google(audio)
                    confidence = getattr(recognizer, 'confidence', 1.0)

                    if confidence >= self.recognition_threshold:
                        print(f"\n🎙️ You said: {command}")
                        self.command_queue.put(("voice", command))
                    else:
                        print(f"Low confidence ({confidence}), ignored: {command}")

                except sr.UnknownValueError:
                    pass  # Ignore unrecognized speech
                except sr.RequestError as e:
                    print(f"Could not request results: {e}")

            except Exception as e:
                print(f"Error in voice listening: {e}")
                time.sleep(1)  # Prevent rapid retries

    def chat_listener(self):
        """Text command listener"""
        while self.running:
            try:
                user_input = input("\nEnter command (or 'help'/'quit'): ")
                if user_input.strip():  # Ignore empty input
                    self.command_queue.put(("chat", user_input))
            except Exception as e:
                print(f"Error in chat input: {e}")

    async def run(self):
        """Run the assistant with enhanced error handling"""
        if not await self.start():
            print("Failed to start assistant. Please check the logs.")
            return

        self.running = True

        # Start voice and chat listeners
        voice_thread = threading.Thread(target=self.voice_listener)
        chat_thread = threading.Thread(target=self.chat_listener)

        voice_thread.daemon = True
        chat_thread.daemon = True

        voice_thread.start()
        chat_thread.start()

        self.voice_manager.speak("AI Debug Assistant is ready! How can I help you today?")
        self.show_help()

        try:
            while self.running:
                try:
                    command_type, command = self.command_queue.get(timeout=1)
                    await self.process_command(command_type, command)
                except queue.Empty:
                    continue  # No command to process
                except Exception as e:
                    print(f"Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\nReceived interrupt signal...")
            self.voice_manager.speak("Shutting down gracefully...")
        finally:
            self.running = False
            print("\nCleaning up...")
            self.voice_manager.shutdown()
            self.server_manager.stop_server()
            print("Shutdown complete. Goodbye!")


if __name__ == "__main__":
    # Set up console title
    if os.name == 'nt':  # Windows
        os.system('title AI Debug Assistant')
    else:  # Unix/Linux/MacOS
        print('\33]0;AI Debug Assistant\a', end='', flush=True)

    print("""
    ================================
    🤖 AI Debug Assistant Starting...
    ================================
    """)

    assistant = DebugAssistantClient()
    asyncio.run(assistant.run())