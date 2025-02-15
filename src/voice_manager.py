import pyttsx3
import threading
import queue
import keyboard
import re
from typing import List


class EnhancedVoiceManager:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speaking rate
        self.engine.setProperty('volume', 0.9)  # Volume level

        # State management
        self.speaking = False
        self.paused = False
        self.speech_queue = queue.Queue()
        self.stop_speaking = threading.Event()

        # Start speech thread
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

        # Set up keyboard shortcuts
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        """Setup keyboard shortcuts for voice control"""
        try:
            keyboard.add_hotkey('ctrl+shift+space', self.interrupt_speech)  # Stop
            keyboard.add_hotkey('ctrl+shift+r', self.resume_speech)  # Resume
            keyboard.add_hotkey('ctrl+shift+up', self.increase_volume)  # Volume up
            keyboard.add_hotkey('ctrl+shift+down', self.decrease_volume)  # Volume down
            keyboard.add_hotkey('ctrl+shift+left', self.decrease_rate)  # Slow down
            keyboard.add_hotkey('ctrl+shift+right', self.increase_rate)  # Speed up
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")

    def _speech_worker(self):
        """Background worker for speech processing"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break

                self.speaking = True
                self.stop_speaking.clear()

                # Break text into smaller chunks for better interrupt response
                chunks = self._chunk_text(text)

                for chunk in chunks:
                    # Check if paused
                    while self.paused:
                        if self.stop_speaking.is_set():
                            break
                        threading.Event().wait(0.1)

                    # Check if stopped
                    if self.stop_speaking.is_set():
                        break

                    # Speak the chunk
                    self.engine.say(chunk)
                    self.engine.runAndWait()

                self.speaking = False

            except Exception as e:
                print(f"Speech error: {e}")
                self.speaking = False

    def _chunk_text(self, text: str) -> List[str]:
        """Break text into smaller, natural chunks"""
        # Split by sentences first
        chunks = re.split(r'(?<=[.!?])\s+', text)

        # Further split long sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > 100:  # If chunk is too long
                words = chunk.split()
                sub_chunks = []
                current_chunk = []

                for word in words:
                    current_chunk.append(word)
                    if len(' '.join(current_chunk)) > 80:  # Target chunk size
                        sub_chunks.append(' '.join(current_chunk))
                        current_chunk = []

                if current_chunk:
                    sub_chunks.append(' '.join(current_chunk))
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)

        return final_chunks

    def speak(self, text: str):
        """Add text to speech queue"""
        if text:
            print("\n🤖 Assistant:", text)
            self.speech_queue.put(text)

    def interrupt_speech(self):
        """Interrupt current speech"""
        if self.speaking:
            self.stop_speaking.set()
            self.paused = True
            try:
                self.engine.stop()
            except:
                pass
            self.speaking = False
            print("\nSpeech interrupted!")

    def resume_speech(self):
        """Resume speech from where it was paused"""
        if self.paused:
            self.paused = False
            print("\nSpeech resumed!")

    def increase_volume(self):
        """Increase speech volume"""
        try:
            current = self.engine.getProperty('volume')
            new_volume = min(1.0, current + 0.1)
            self.engine.setProperty('volume', new_volume)
            print(f"\nVolume increased to {int(new_volume * 100)}%")
        except Exception as e:
            print(f"Error adjusting volume: {e}")

    def decrease_volume(self):
        """Decrease speech volume"""
        try:
            current = self.engine.getProperty('volume')
            new_volume = max(0.0, current - 0.1)
            self.engine.setProperty('volume', new_volume)
            print(f"\nVolume decreased to {int(new_volume * 100)}%")
        except Exception as e:
            print(f"Error adjusting volume: {e}")

    def increase_rate(self):
        """Increase speech rate"""
        try:
            current = self.engine.getProperty('rate')
            new_rate = current + 25
            self.engine.setProperty('rate', new_rate)
            print(f"\nSpeech rate increased to {new_rate}")
        except Exception as e:
            print(f"Error adjusting rate: {e}")

    def decrease_rate(self):
        """Decrease speech rate"""
        try:
            current = self.engine.getProperty('rate')
            new_rate = max(50, current - 25)
            self.engine.setProperty('rate', new_rate)
            print(f"\nSpeech rate decreased to {new_rate}")
        except Exception as e:
            print(f"Error adjusting rate: {e}")

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

    def set_voice(self, voice_id=None):
        """Set a specific voice (if available)"""
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                if voice_id is not None and 0 <= voice_id < len(voices):
                    self.engine.setProperty('voice', voices[voice_id].id)
                    print(f"\nVoice changed to: {voices[voice_id].name}")
                else:
                    # List available voices
                    print("\nAvailable voices:")
                    for idx, voice in enumerate(voices):
                        print(f"{idx}: {voice.name}")
        except Exception as e:
            print(f"Error setting voice: {e}")

    def get_current_settings(self):
        """Get current voice settings"""
        try:
            settings = {
                'volume': self.engine.getProperty('volume'),
                'rate': self.engine.getProperty('rate'),
                'voice': self.engine.getProperty('voice'),
                'voices': [voice.name for voice in self.engine.getProperty('voices')]
            }
            return settings
        except Exception as e:
            print(f"Error getting settings: {e}")
            return None