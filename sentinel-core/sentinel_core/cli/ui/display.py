"""
Display Components

Rich UI components for displaying information.
"""

from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from ..console import console


def show_diff(before: str, after: str, title: str = "Change"):
    """
    Show before/after diff.
    
    Args:
        before: Original value/path
        after: New value/path
        title: Panel title
    """
    console.print(
        Panel(
            f"[muted]{before}[/] → [highlight]{after}[/]",
            title=title,
            border_style="cyan"
        )
    )


def show_error(message: str, details: str = None):
    """
    Display error message.
    
    Args:
        message: Error message
        details: Additional error details
    """
    console.print(f"[error]❌ Error:[/] {message}")
    if details:
        console.print(f"[muted]{details}[/]")


def show_success(message: str, details: str = None):
    """
    Display success message.
    
    Args:
        message: Success message
        details: Additional details
    """
    console.print(f"[success]✓ {message}[/]")
    if details:
        console.print(f"[muted]{details}[/]")


def show_warning(message: str, details: str = None):
    """
    Display warning message.
    
    Args:
        message: Warning message
        details: Additional details
    """
    console.print(f"[warning]⚠ Warning:[/] {message}")
    if details:
        console.print(f"[muted]{details}[/]")


def show_info(message: str):
    """
    Display info message.
    
    Args:
        message: Info message
    """
    console.print(f"[info]ℹ {message}[/]")


def show_code(code: str, language: str = "python", title: str = None):
    """
    Display syntax-highlighted code.
    
    Args:
        code: Code to display
        language: Programming language for syntax highlighting
        title: Optional title
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    
    if title:
        console.print(Panel(syntax, title=title, border_style="cyan"))
    else:
        console.print(syntax)


def create_table(title: str, columns: list) -> Table:
    """
    Create a styled table.
    
    Args:
        title: Table title
        columns: List of (name, kwargs) tuples for columns
        
    Returns:
        Rich Table instance
        
    Example:
        >>> table = create_table("Files", [
        ...     ("Name", {"style": "cyan"}),
        ...     ("Size", {"justify": "right"})
        ... ])
        >>> table.add_row("file.txt", "1.2 MB")
        >>> console.print(table)
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
    )
    
    for col_name, col_kwargs in columns:
        table.add_column(col_name, **col_kwargs)
    
    return table
