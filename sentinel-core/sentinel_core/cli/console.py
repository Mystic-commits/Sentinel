"""
Rich Console with Sentinel Theme

Shared console instance for consistent styling across all CLI commands.
"""

from rich.console import Console
from rich.theme import Theme

# Sentinel color theme
sentinel_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "muted": "dim",
    "highlight": "bold cyan",
    "path": "blue underline",
    "count": "bold magenta",
    "progress.description": "cyan",
})

# Shared console instance
console = Console(theme=sentinel_theme)
