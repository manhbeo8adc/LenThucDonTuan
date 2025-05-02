"""
Application constants and environment information.
"""
import platform
import os

# System information
SYSTEM_OS = platform.system().lower()
IS_WINDOWS = SYSTEM_OS == "windows"
IS_LINUX = SYSTEM_OS == "linux"
IS_MAC = SYSTEM_OS == "darwin"

# Shell information
SHELL_TYPE = "powershell" if IS_WINDOWS else "bash"
COMMAND_SEPARATOR = ";" if IS_WINDOWS else "&&"

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# Create directories if they don't exist
for directory in [DATA_DIR, CONFIG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory) 