"""
Plan Preview Module

Converts PlanSchema into human-readable previews for terminal and web output.
Provides transparent visibility into pending file operations before execution.
"""

from typing import Dict, List, Any
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from sentinel_core.models.planner import PlanSchema, PlanAction, AmbiguousFile
from sentinel_core.models.enums import ActionType


def generate_terminal_preview(plan: PlanSchema) -> str:
    """
    Generate a Rich-formatted terminal preview of a plan.
    
    Args:
        plan: The PlanSchema to preview
        
    Returns:
        Rich-formatted string ready for console.print()
        
    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> preview = generate_terminal_preview(plan)
        >>> console.print(preview)
    """
    console = Console(record=True, width=100)
    
    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Plan Preview[/bold cyan]\n"
        f"[dim]Task ID:[/dim] {plan.task_id}\n"
        f"[dim]Scope:[/dim] {plan.scope_path}\n"
        f"[dim]Summary:[/dim] {plan.summary}",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    # Group actions by type
    actions_by_type = _group_actions_by_type(plan.actions)
    
    # Folders to create
    if plan.folders_to_create:
        console.print("[bold cyan]📁 Folders to Create[/bold cyan]")
        for folder in plan.folders_to_create:
            short_path = _shorten_path(folder, plan.scope_path)
            console.print(f"  [cyan]+[/cyan] {short_path}")
        console.print()
    
    # Move operations
    if ActionType.MOVE in actions_by_type:
        console.print("[bold blue]➜  Move Operations[/bold blue]")
        for action in actions_by_type[ActionType.MOVE]:
            src = _shorten_path(action.source_path, plan.scope_path)
            dst = _shorten_path(action.destination_path, plan.scope_path)
            confidence_color = _get_confidence_color(action.confidence)
            console.print(
                f"  [blue]→[/blue] {src} [dim]→[/dim] {dst} "
                f"[{confidence_color}]({action.confidence:.0%})[/{confidence_color}]"
            )
            console.print(f"    [dim italic]{action.reason}[/dim italic]")
        console.print()
    
    # Rename operations
    if ActionType.RENAME in actions_by_type:
        console.print("[bold magenta]✎  Rename Operations[/bold magenta]")
        for action in actions_by_type[ActionType.RENAME]:
            src = _shorten_path(action.source_path, plan.scope_path)
            dst = _shorten_path(action.destination_path, plan.scope_path)
            confidence_color = _get_confidence_color(action.confidence)
            console.print(
                f"  [magenta]⟲[/magenta] {src} [dim]→[/dim] {dst} "
                f"[{confidence_color}]({action.confidence:.0%})[/{confidence_color}]"
            )
            console.print(f"    [dim italic]{action.reason}[/dim italic]")
        console.print()
    
    # Delete operations (highlighted for safety)
    if ActionType.DELETE in actions_by_type:
        console.print("[bold red]🗑️  Delete Operations[/bold red]")
        for action in actions_by_type[ActionType.DELETE]:
            src = _shorten_path(action.source_path, plan.scope_path)
            confidence_color = _get_confidence_color(action.confidence)
            console.print(
                f"  [red bold]✗[/red bold] {src} "
                f"[{confidence_color}]({action.confidence:.0%})[/{confidence_color}]"
            )
            console.print(f"    [dim italic]{action.reason}[/dim italic]")
        console.print()
    
    # Skip operations
    if ActionType.SKIP in actions_by_type:
        console.print("[bold dim]⊘  Skipped Files[/bold dim]")
        for action in actions_by_type[ActionType.SKIP]:
            src = _shorten_path(action.source_path, plan.scope_path)
            console.print(
                f"  [dim]○[/dim] {src}"
            )
            console.print(f"    [dim italic]{action.reason}[/dim italic]")
        console.print()
    
    # Ambiguous files (needs manual review)
    if plan.ambiguous_files:
        console.print("[bold yellow]⚠️  Ambiguous Files (Manual Review Required)[/bold yellow]")
        for ambiguous in plan.ambiguous_files:
            short_path = _shorten_path(ambiguous.path, plan.scope_path)
            console.print(f"  [yellow]?[/yellow] {short_path}")
            console.print(f"    [dim italic]{ambiguous.reason}[/dim italic]")
            if ambiguous.suggested_action:
                console.print(f"    [dim]Suggested: {ambiguous.suggested_action.value}[/dim]")
        console.print()
    
    # Statistics footer
    stats = _calculate_stats(plan)
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column(justify="right", style="dim")
    stats_table.add_column(justify="left")
    
    stats_table.add_row("Total Actions:", f"[bold]{stats['total_actions']}[/bold]")
    if stats['folders'] > 0:
        stats_table.add_row("Folders:", f"[cyan]{stats['folders']}[/cyan]")
    if stats['moves'] > 0:
        stats_table.add_row("Moves:", f"[blue]{stats['moves']}[/blue]")
    if stats['renames'] > 0:
        stats_table.add_row("Renames:", f"[magenta]{stats['renames']}[/magenta]")
    if stats['deletes'] > 0:
        stats_table.add_row("Deletes:", f"[red bold]{stats['deletes']}[/red bold]")
    if stats['skips'] > 0:
        stats_table.add_row("Skips:", f"[dim]{stats['skips']}[/dim]")
    if stats['ambiguous'] > 0:
        stats_table.add_row("Ambiguous:", f"[yellow]{stats['ambiguous']}[/yellow]")
    stats_table.add_row("Avg Confidence:", f"{stats['avg_confidence']:.0%}")
    
    console.print(Panel(stats_table, title="[bold]Summary[/bold]", border_style="dim"))
    console.print()
    
    return console.export_text()


def generate_web_preview(plan: PlanSchema) -> Dict[str, Any]:
    """
    Generate a structured JSON preview for web UI consumption.
    
    Args:
        plan: The PlanSchema to preview
        
    Returns:
        Dictionary with structured operation data and statistics
        
    Example:
        >>> preview = generate_web_preview(plan)
        >>> print(preview['stats']['total_actions'])
    """
    actions_by_type = _group_actions_by_type(plan.actions)
    
    operations = {
        "folders_to_create": plan.folders_to_create,
        "moves": [
            {
                "from": action.source_path,
                "to": action.destination_path,
                "reason": action.reason,
                "confidence": action.confidence
            }
            for action in actions_by_type.get(ActionType.MOVE, [])
        ],
        "renames": [
            {
                "from": action.source_path,
                "to": action.destination_path,
                "reason": action.reason,
                "confidence": action.confidence
            }
            for action in actions_by_type.get(ActionType.RENAME, [])
        ],
        "deletes": [
            {
                "path": action.source_path,
                "reason": action.reason,
                "confidence": action.confidence
            }
            for action in actions_by_type.get(ActionType.DELETE, [])
        ],
        "skips": [
            {
                "path": action.source_path,
                "reason": action.reason,
                "confidence": action.confidence
            }
            for action in actions_by_type.get(ActionType.SKIP, [])
        ],
    }
    
    ambiguous = [
        {
            "path": amb.path,
            "reason": amb.reason,
            "suggested_action": amb.suggested_action.value if amb.suggested_action else None
        }
        for amb in plan.ambiguous_files
    ]
    
    stats = _calculate_stats(plan)
    
    return {
        "task_id": plan.task_id,
        "scope_path": plan.scope_path,
        "summary": plan.summary,
        "operations": operations,
        "ambiguous_files": ambiguous,
        "stats": stats
    }


# Helper functions

def _group_actions_by_type(actions: List[PlanAction]) -> Dict[ActionType, List[PlanAction]]:
    """Group actions by their type."""
    grouped = defaultdict(list)
    for action in actions:
        grouped[action.type].append(action)
    return dict(grouped)


def _calculate_stats(plan: PlanSchema) -> Dict[str, Any]:
    """Calculate statistics for a plan."""
    actions_by_type = _group_actions_by_type(plan.actions)
    
    total_actions = len(plan.actions)
    avg_confidence = (
        sum(action.confidence for action in plan.actions) / total_actions
        if total_actions > 0
        else 0.0
    )
    
    return {
        "total_actions": total_actions,
        "folders": len(plan.folders_to_create),
        "moves": len(actions_by_type.get(ActionType.MOVE, [])),
        "renames": len(actions_by_type.get(ActionType.RENAME, [])),
        "deletes": len(actions_by_type.get(ActionType.DELETE, [])),
        "skips": len(actions_by_type.get(ActionType.SKIP, [])),
        "ambiguous": len(plan.ambiguous_files),
        "avg_confidence": avg_confidence
    }


def _shorten_path(path: str, scope_path: str) -> str:
    """
    Shorten a path for readability by making it relative to scope if possible.
    
    Args:
        path: Full path to shorten
        scope_path: The scope path to make relative to
        
    Returns:
        Shortened path string
    """
    if not path:
        return ""
    
    try:
        path_obj = Path(path)
        scope_obj = Path(scope_path)
        
        # Try to make relative
        if path_obj.is_relative_to(scope_obj):
            rel_path = path_obj.relative_to(scope_obj)
            return f"./{rel_path}"
    except (ValueError, AttributeError):
        # If relative_to fails, just return the path
        pass
    
    return path


def _get_confidence_color(confidence: float) -> str:
    """
    Get a color based on confidence level.
    
    Args:
        confidence: Confidence value between 0 and 1
        
    Returns:
        Rich color name
    """
    if confidence >= 0.9:
        return "green"
    elif confidence >= 0.7:
        return "yellow"
    else:
        return "red"
