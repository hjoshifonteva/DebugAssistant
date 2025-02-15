import os
import re
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import hashlib


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove any potentially harmful characters
    text = re.sub(r'[^\w\s\-\.]', '', text)
    return text.strip()


def format_error_message(error: Exception) -> str:
    """Format error message for display"""
    return f"{type(error).__name__}: {str(error)}"


def load_json_file(filepath: str) -> Optional[Dict]:
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None


def save_json_file(data: Dict, filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def format_bytes(bytes: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"


def check_file_exists(filepath: str) -> bool:
    """Check if file exists and is accessible"""
    return os.path.exists(filepath) and os.access(filepath, os.R_OK)


def create_directory_if_not_exists(directory: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get file information"""
    try:
        stats = os.stat(filepath)
        return {
            "size": format_bytes(stats.st_size),
            "created": format_timestamp(stats.st_ctime),
            "modified": format_timestamp(stats.st_mtime),
            "accessed": format_timestamp(stats.st_atime),
            "is_dir": os.path.isdir(filepath),
            "extension": os.path.splitext(filepath)[1],
            "permissions": oct(stats.st_mode)[-3:]
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {}


def parse_command_args(command: str) -> Dict[str, Any]:
    """Parse command arguments"""
    args = {}
    parts = command.split()

    i = 0
    while i < len(parts):
        if parts[i].startswith('--'):
            key = parts[i][2:]
            if i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                args[key] = parts[i + 1]
                i += 2
            else:
                args[key] = True
                i += 1
        else:
            i += 1

    return args


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def generate_file_hash(filepath: str, algorithm: str = 'sha256') -> Optional[str]:
    """Generate hash of file contents"""
    try:
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error generating file hash: {e}")
        return None


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def retry_operation(func: callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Retry an operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = delay * (2 ** attempt)
            print(f"Operation failed: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)


def validate_file_path(filepath: str) -> bool:
    """Validate file path"""
    try:
        # Check if path is absolute
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(filepath)

        # Check if parent directory exists
        parent_dir = os.path.dirname(filepath)
        if not os.path.exists(parent_dir):
            return False

        # Check if path is within allowed directories
        allowed_dirs = [os.path.expanduser('~'), '/tmp', './']
        return any(os.path.commonpath([filepath, allowed]) == allowed
                   for allowed in allowed_dirs)
    except Exception:
        return False


def format_list_for_display(items: List[Any], separator: str = ', ') -> str:
    """Format list for display with proper grammar"""
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{separator.join(str(x) for x in items[:-1])} and {items[-1]}"


def chunked_read(filepath: str, chunk_size: int = 8192) -> Union[str, bytes]:
    """Read file in chunks to handle large files"""
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        print(f"Error reading file: {e}")
        yield b""


def safe_delete(filepath: str) -> bool:
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_unique_filename(filepath: str) -> str:
    """Get unique filename by appending number if file exists"""
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    counter = 1
    while True:
        new_filepath = f"{base}_{counter}{ext}"
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1