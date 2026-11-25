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


def show_watchkeeper() -> None:
    """Greet interactive users without changing piped output."""
    if console.is_terminal:
        from rich.columns import Columns
        from rich.text import Text

        mascot = Text(" /---\\\n| o o |\n \\_v_/ ", style="bright_green")
        title = Text.assemble(("Sentinel\n", "bold"), ("Local file workspace", "muted"))
        console.print(Columns([mascot, title], padding=(0, 2)))


def watch_status(message: str):
    """Use the shared terminal activity indicator while a command runs."""
    return console.status(message, spinner="dots", spinner_style="bright_green")
