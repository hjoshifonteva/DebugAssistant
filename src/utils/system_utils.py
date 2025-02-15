import os
import psutil
import platform
import shutil
from typing import Optional, List, Dict
import winreg
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


def get_system_info() -> Dict:
    """Get system information"""
    try:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}


def find_executable(name: str, possible_locations: List[str]) -> Optional[str]:
    """Find executable in common locations"""
    try:
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
    except Exception as e:
        logger.error(f"Error finding executable {name}: {e}")
        return None


def get_registry_value(key_path: str, value_name: str = None) -> Optional[str]:
    """Get a value from Windows registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value = winreg.QueryValue(key, value_name)
        winreg.CloseKey(key)
        return value
    except Exception as e:
        logger.error(f"Error reading registry: {e}")
        return None


def create_directory_structure(base_path: str, structure: List[str]) -> bool:
    """Create a directory structure"""
    try:
        for dir_name in structure:
            path = os.path.join(base_path, dir_name)
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory structure: {e}")
        return False


def is_process_running(process_name: str) -> bool:
    """Check if a process is running"""
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking process {process_name}: {e}")
        return False


def kill_process(process_name: str) -> bool:
    """Kill a process by name"""
    try:
        killed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                proc.kill()
                killed = True
        return killed
    except Exception as e:
        logger.error(f"Error killing process {process_name}: {e}")
        return False


def get_memory_usage() -> Dict:
    """Get detailed memory usage information"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return {}


def get_disk_usage(path: str = "/") -> Dict:
    """Get disk usage information"""
    try:
        usage = psutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return {}


def get_network_info() -> Dict:
    """Get network information"""
    try:
        network_info = {}
        for interface, addresses in psutil.net_if_addrs().items():
            network_info[interface] = []
            for addr in addresses:
                network_info[interface].append({
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "family": str(addr.family)
                })
        return network_info
    except Exception as e:
        logger.error(f"Error getting network info: {e}")
        return {}


def get_cpu_usage() -> Dict:
    """Get CPU usage information"""
    try:
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": {
                "physical": psutil.cpu_count(logical=False),
                "logical": psutil.cpu_count(logical=True)
            },
            "frequency": {
                "current": psutil.cpu_freq().current,
                "min": psutil.cpu_freq().min,
                "max": psutil.cpu_freq().max
            }
        }
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
        return {}


def get_battery_info() -> Dict:
    """Get battery information if available"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": battery.secsleft if battery.secsleft != -1 else None
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting battery info: {e}")
        return {}


def get_system_uptime() -> str:
    """Get system uptime"""
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        return str(datetime.fromtimestamp(psutil.boot_time()))
    except Exception as e:
        logger.error(f"Error getting system uptime: {e}")
        return ""


def create_log_directory() -> str:
    """Create and return path to log directory"""
    try:
        log_dir = os.path.join(os.path.expanduser("~"), ".ai_debug_assistant", "logs")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception as e:
        logger.error(f"Error creating log directory: {e}")
        return ""


def setup_logging(log_dir: str = None):
    """Setup logging configuration"""
    try:
        if not log_dir:
            log_dir = create_log_directory()

        log_file = os.path.join(log_dir, f"debug_assistant_{datetime.now().strftime('%Y%m%d')}.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        print(f"Error setting up logging: {e}")


def check_system_requirements() -> Dict:
    """Check if system meets minimum requirements"""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_count = psutil.cpu_count()

        requirements = {
            "memory": memory.total >= 4 * 1024 * 1024 * 1024,  # 4GB RAM
            "disk": disk.free >= 1 * 1024 * 1024 * 1024,  # 1GB free space
            "cpu": cpu_count >= 2,  # At least 2 cores
            "python_version": platform.python_version_tuple()
        }

        return {
            "meets_requirements": all(requirements.values()),
            "details": requirements
        }
    except Exception as e:
        logger.error(f"Error checking system requirements: {e}")
        return {"meets_requirements": False, "error": str(e)}