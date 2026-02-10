import sys
from pathlib import Path

def _get_system_protected_paths():
    """Returns a set of protected paths based on the OS."""
    if sys.platform == "darwin":  # macOS
        return {
            Path("/System"),
            Path("/usr"),
            Path("/bin"),
            Path("/sbin"),
            Path("/var"),
            Path("/etc"),
            Path("/Applications"),
            Path("/Library"),
            Path("/boot"),
        }
    elif sys.platform == "win32":  # Windows
        return {
            Path("C:\\Windows"),
            Path("C:\\Program Files"),
            Path("C:\\Program Files (x86)"),
            Path("C:\\System Volume Information"),
        }
    else: # Linux/Other (Fallback)
        return {
             Path("/usr"),
             Path("/bin"),
             Path("/sbin"),
             Path("/var"),
             Path("/etc"),
             Path("/boot"),
             Path("/sys"),
             Path("/proc"),
        }

PROTECTED_PATHS = _get_system_protected_paths()

CRITICAL_EXTENSIONS = {
    ".sys", ".dll", ".exe", ".app", ".bat", ".cmd", ".sh", ".py", ".js", ".json", ".xml", ".ini"
} # Mostly focusing on preventing accidental rename/move of executable code or config as "Misc"

