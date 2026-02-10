"""
Confirmation Prompts

User interaction prompts with Rich styling.
"""

from rich.prompt import Confirm, Prompt
from ..console import console


def confirm(message: str, default: bool = False) -> bool:
    """
    Show a confirmation prompt.
    
    Args:
        message: Question to ask user
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirmed, False otherwise
        
    Example:
        >>> if confirm("Delete these files?"):
        ...     perform_deletion()
    """
    return Confirm.ask(
        f"[highlight]{message}[/]",
        default=default,
        console=console
    )


def ask_text(message: str, default: str = "") -> str:
    """
    Ask user for text input.
    
    Args:
        message: Prompt message
        default: Default value
        
    Returns:
        User's input text
        
    Example:
        >>> name = ask_text("Enter task name", default="My Task")
    """
    return Prompt.ask(
        f"[highlight]{message}[/]",
        default=default,
        console=console
    )


def ask_choice(message: str, choices: list, default: str = None) -> str:
    """
    Ask user to choose from a list.
    
    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice
        
    Returns:
        User's selected choice
        
    Example:
        >>> action = ask_choice("What to do?", ["keep", "delete", "move"])
    """
    return Prompt.ask(
        f"[highlight]{message}[/]",
        choices=choices,
        default=default,
        console=console
    )
