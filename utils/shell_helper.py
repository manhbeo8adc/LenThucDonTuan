"""
Shell command helper utilities.
"""
import platform
import subprocess


def get_shell_type():
    """Get the current shell type based on the platform."""
    system = platform.system().lower()
    if system == "windows":
        return "powershell"
    return "bash"


def format_command(command, shell_type=None):
    """Format command based on shell type."""
    if shell_type is None:
        shell_type = get_shell_type()
    
    if shell_type == "powershell":
        # PowerShell uses ; for command chaining
        return command.replace("&&", ";")
    return command


def run_command(command, cwd=None, shell_type=None):
    """Run a shell command with proper formatting."""
    formatted_cmd = format_command(command, shell_type)
    
    try:
        if platform.system().lower() == "windows":
            # Use PowerShell on Windows
            process = subprocess.Popen(
                ["powershell", "-Command", formatted_cmd],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            # Use bash on Unix-like systems
            process = subprocess.Popen(
                ["bash", "-c", formatted_cmd],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        stdout, stderr = process.communicate()
        return {
            "success": process.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": process.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        } 