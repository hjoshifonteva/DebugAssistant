from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7

    # Voice Settings
    SPEECH_RATE: int = 150
    SPEECH_VOLUME: float = 0.9
    VOICE_RECOGNITION_THRESHOLD: float = 0.7

    # System Settings
    MAX_MEMORY: int = 1000  # Maximum items in working memory
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "debug_assistant.log"

    # Database Settings
    DB_PATH: str = "debug_memory.db"
    CLEANUP_DAYS: int = 30  # Days to keep debug sessions

    # Server Settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Path Settings
    LOG_DIR: str = os.path.join(os.path.expanduser("~"), ".ai_debug_assistant", "logs")
    DATA_DIR: str = os.path.join(os.path.expanduser("~"), ".ai_debug_assistant", "data")

    # Browser Settings
    SUPPORTED_BROWSERS: list = ["chrome", "firefox"]
    DEFAULT_BROWSER: str = "chrome"
    BROWSER_TIMEOUT: int = 30  # seconds

    # Command Settings
    COMMAND_HISTORY_SIZE: int = 100
    COMMAND_TIMEOUT: int = 60  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True

    def initialize_directories(self):
        """Create necessary directories"""
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def save_to_env(self):
        """Save current settings to .env file"""
        with open(".env", "w") as f:
            for field_name, field_value in self.dict().items():
                if isinstance(field_value, (str, int, float, bool)):
                    f.write(f"{field_name}={field_value}\n")


settings = Settings()
settings.initialize_directories()