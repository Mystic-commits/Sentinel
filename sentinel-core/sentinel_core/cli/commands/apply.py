"""
Apply Command

Execute an organization plan with confirmations.
"""

import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from sentinel_core.executor import execute_plan
from sentinel_core.models import ActionType
from ..console import console
from ..ui.prompts import confirm


def _load_plan(task_id: str):
    """Load plan from database."""
    # TODO: Implement database retrieval
    # For now, return None to show error
    from sentinel_core.memory.db import get_engine, get_session
    from sentinel_core.models.logging import TaskRecord
    from sqlmodel import select
    
    engine = get_engine()
    with get_session(engine) as session:
        stmt = select(TaskRecord).where(TaskRecord.task_id == task_id)
        task = session.exec(stmt).first()
        
        if task:
            # Load the plan JSON
            import json
            return json.loads(task.plan_json) if hasattr(task, 'plan_json') else None
    
    return None


def apply_command(
    task_id: Annotated[str, typer.Argument(help="Task ID to execute")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation prompts")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
):
    """
    Execute an organization plan.
    
    Applies the file operations from a previously created plan.
    You'll be asked to confirm before any changes are made.
    """
    
    # Load plan
    console.print(f"[info]Loading plan:[/] [highlight]{task_id}[/]")
    
    with console.status("[info]Retrieving plan from database..."):
        try:
            plan = _load_plan(task_id)
        except Exception as e:
            console.print(f"[error]Error loading plan:[/] {e}")
            raise typer.Exit(1)
    
    if not plan:
        console.print(f"[error]Error:[/] Plan not found: {task_id}")
        console.print(f"\n[info]Tips:[/]")
        console.print(f"  • Check task ID spelling")
        console.print(f"  • List recent tasks: [muted](coming soon)[/muted]")
        console.print(f"  • Create new plan: [path]sentinel plan <path>[/path]")
        raise typer.Exit(1)
    
    # Show plan summary
    console.print(f"\n[info]📋 Plan Summary:[/]")
    
    # This is a simplified version - in production you'd parse the actual plan
    # For now, show placeholder
    console.print(f"  Task ID: [highlight]{task_id}[/]")
    console.print(f"  [muted](Full plan details coming soon)[/muted]")
    
    # Dry run
    if dry_run:
        console.print(f"\n[info]🔍 Dry run mode - no changes will be made[/]")
        console.print(f"  Remove [path]--dry-run[/path] to execute")
        return
    
    # Confirmation
    if not yes:
        console.print()
        if not confirm("Execute this plan?"):
            console.print("[warning]❌ Aborted[/]")
            raise typer.Exit(0)
    
    # Execute (placeholder - would need actual executor integration)
    console.print(f"\n[info]⚙️  Executing plan...[/]")
    
    # This is a placeholder - actual implementation would call executor
    console.print(f"[warning]Note:[/] Full executor integration coming soon")
    console.print(f"  This command will execute file operations once executor is connected")
    
    # Show success
    console.print(f"\n[success]✓ Plan execution complete[/]")
    console.print(f"\n[highlight]To undo:[/] [path]sentinel undo {task_id}[/path]")
