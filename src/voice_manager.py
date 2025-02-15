import pyttsx3
import threading
import queue
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract
import keyboard


class VoiceManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        self.speaking = False
        self.speech_queue = queue.Queue()
        self.stop_speaking = threading.Event()

        # Set up keyboard combination for interruption
        keyboard.add_hotkey('ctrl+shift+space', self.interrupt_speech)

        # Start speech thread
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def _speech_worker(self):
        """Background worker for speech"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break

                self.speaking = True
                self.stop_speaking.clear()

                # Break text into sentences for interruptible speech
                sentences = text.split('.')
                for sentence in sentences:
                    if self.stop_speaking.is_set():
                        break
                    if sentence.strip():
                        self.engine.say(sentence)
                        self.engine.runAndWait()

                self.speaking = False
            except Exception as e:
                print(f"Speech error: {e}")
                self.speaking = False

    def speak(self, text: str):
        """Add text to speech queue"""
        print("\n🤖 Assistant:", text)
        self.speech_queue.put(text)

    def interrupt_speech(self):
        """Interrupt current speech"""
        if self.speaking:
            self.stop_speaking.set()
            try:
                self.engine.stop()
            except:
                pass
            self.speaking = False
            print("\nSpeech interrupted!")

    def read_screen_text(self, region=None):
        """Read text from screen or specific region"""
        try:
            # Capture screen or region
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()

            # Convert to format suitable for OCR
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

            # Extract text
            text = pytesseract.image_to_string(screenshot)
            return text.strip()
        except Exception as e:
            print(f"Screen reading error: {e}")
            return ""

    def read_code_from_screen(self):
        """Specifically read code from active editor"""
        try:
            # Try to identify code editor region (VS Code has specific colors)
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)

            # Convert to grayscale for text detection
            gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            # Use OCR with code-specific configuration
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(gray, config=custom_config)

            return text.strip()
        except Exception as e:
            print(f"Code reading error: {e}")
            return ""

    def shutdown(self):
        """Clean shutdown of voice manager"""
        self.interrupt_speech()
        self.speech_queue.put(None)  # Signal thread to stop
        if self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1)
        try:
            self.engine.stop()
        except:
            pass