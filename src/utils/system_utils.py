import os
import winreg
import psutil
from typing import Optional, List

def find_executable(name: str, possible_locations: List[str]) -> Optional[str]:
    """Find executable in common locations"""
    # Check PATH
    path_exe = shutil.which(name)
    if path_exe:
        return path_exe

    # Check common locations
    for location in possible_locations:
        expanded_path = os.path.expandvars(location)
        if os.path.exists(expanded_path):
            return expanded_path

    return None

def is_process_running(process_name: str) -> bool:
    """Check if a process is running"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def kill_process(process_name: str) -> bool:
    """Kill a process by name"""
    killed = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                proc.kill()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed

def get_registry_value(key_path: str, value_name: str = None) -> Optional[str]:
    """Get a value from Windows registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value = winreg.QueryValue(key, value_name)
        winreg.CloseKey(key)
        return value
    except:
        return None

def create_directory_structure(base_path: str, structure: List[str]) -> bool:
    """Create a directory structure"""
    try:
        for dir_name in structure:
            path = os.path.join(base_path, dir_name)
            os.makedirs(path, exist_ok=True)
        return True
    except:
        return False