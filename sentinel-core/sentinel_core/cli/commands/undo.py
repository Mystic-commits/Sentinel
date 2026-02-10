"""
Undo Command

Undo previously executed operations.
"""

import typer
from typing_extensions import Annotated

from sentinel_core.executor import UndoManager
from sentinel_core.memory.db import get_engine, get_session
from ..console import console
from ..ui.prompts import confirm


def undo_command(
    task_id: Annotated[str, typer.Argument(help="Task ID to undo")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """
    Undo a previously executed task.
    
    Reverses file operations from a completed task.
    Note: Delete operations cannot be undone if files were permanently removed.
    """
    
    console.print(f"[info]🔄 Checking undo status for:[/] [highlight]{task_id}[/]")
    
    # Get database connection
    try:
        engine = get_engine()
    except Exception as e:
        console.print(f"[error]Error connecting to database:[/] {e}")
        raise typer.Exit(1)
    
    with get_session(engine) as session:
        undo_mgr = UndoManager(session)
        
        # Check if task can be undone
        try:
            can_undo, reason = undo_mgr.can_undo_task(task_id)
        except Exception as e:
            console.print(f"[error]Error checking undo status:[/] {e}")
            raise typer.Exit(1)
        
        if not can_undo:
            console.print(f"\n[error]❌ Cannot undo:[/] {reason}")
            console.print("\n[info]Possible reasons:[/]")
            console.print("  • Task not found")
            console.print("  • Task not yet executed")
            console.print("  • Task already undone")
            console.print("  • Delete operations cannot be fully undone")
            raise typer.Exit(1)
        
        # Get undo operations
        try:
            operations = undo_mgr.get_undo_operations(task_id)
        except Exception as e:
            console.print(f"[error]Error retrieving operations:[/] {e}")
            raise typer.Exit(1)
        
        if not operations:
            console.print("[warning]No operations to undo[/]")
            return
        
        # Show preview
        console.print(f"\n[info]📋 Undo Preview:[/]")
        console.print(f"  Total operations: [count]{len(operations)}[/count]\n")
        
        can_undo_count = 0
        cannot_undo_count = 0
        
        for i, op in enumerate(operations[:10], 1):  # Show first 10
            if op.can_undo:
                can_undo_count += 1
                console.print(
                    f"  [success]✓[/] {op.action_type.value}: "
                    f"[path]{op.new_path}[/] → [path]{op.original_path}[/]"
                )
            else:
                cannot_undo_count += 1
                console.print(
                    f"  [error]✗[/] {op.action_type.value}: "
                    f"{op.undo_reason or 'Cannot undo'}"
                )
        
        if len(operations) > 10:
            remaining = len(operations) - 10
            console.print(f"\n  [muted]... and {remaining} more operations[/]")
        
        # Summary
        console.print(f"\n[info]Summary:[/]")
        console.print(f"  Can undo: [success]{can_undo_count}[/]")
        if cannot_undo_count > 0:
            console.print(f"  Cannot undo: [warning]{cannot_undo_count}[/]")
        
        # Confirm
        if not yes:
            console.print()
            if not confirm("Proceed with undo?"):
                console.print("[warning]❌ Aborted[/]")
                raise typer.Exit(0)
        
        # Perform undo
        console.print(f"\n[info]⚙️  Undoing operations...[/]")
        
        try:
            result = undo_mgr.undo_task(task_id)
        except Exception as e:
            console.print(f"[error]Error during undo:[/] {e}")
            raise typer.Exit(1)
        
        # Show results
        console.print()
        if result.failed_actions > 0:
            console.print(f"[warning]⚠ Partial undo completed[/]")
            console.print(f"  Success: [success]{result.successful_actions}[/]")
            console.print(f"  Failed: [error]{result.failed_actions}[/]")
            
            if result.error_message:
                console.print(f"\n[error]Error details:[/] {result.error_message}")
        else:
            console.print(f"[success]✓ Undo complete![/]")
            console.print(f"  Reversed {result.successful_actions} operations")
        
        console.print(f"\n[muted]Task {task_id} has been undone[/]")
