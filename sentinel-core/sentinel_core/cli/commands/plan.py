"""
Plan Command

Create an AI-powered organization plan.
"""

from pathlib import Path
import typer
from typing_extensions import Annotated

from sentinel_core.scanner import scan_directory
# Import backend functions - gracefully handle if not available
try:
    from sentinel_core.planner import PlannerAgent
    from sentinel_core.preview.preview import generate_terminal_preview
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
from ..console import console


def plan_command(
    path: Annotated[Path, typer.Argument(help="Path to organize", exists=True)] = Path("."),
    prompt: Annotated[str, typer.Option("--prompt", "-p", help="Custom prompt for AI")] = "",
    save: Annotated[bool, typer.Option("--save/--no-save", help="Save plan to database")] = True,
):
    """
    Create an AI-powered organization plan.
    
    Scans the directory and uses AI to suggest how to organize files.
    The plan can be reviewed and executed with 'sentinel apply'.
    """
    
    # Validate path
    if not path.exists():
        console.print(f"[error]Error:[/] Path not found: {path}")
        raise typer.Exit(1)
    
    if not path.is_dir():
        console.print(f"[error]Error:[/] Not a directory: {path}")
        raise typer.Exit(1)
    
    # Step 1: Scan
    console.print(f"[info]📂 Scanning:[/] [path]{path.absolute()}[/path]")
    
    with console.status("[info]Analyzing files..."):
        try:
            scan_result = scan_directory(str(path.absolute()))
        except Exception as e:
            console.print(f"[error]Error during scan:[/] {e}")
            raise typer.Exit(1)
    
    if scan_result.total_files == 0:
        console.print("[warning]No files found to organize[/]")
        return
    
    console.print(f"[success]✓ Found {scan_result.total_files} files[/]\n")
    
    # Check backend availability
    if not BACKEND_AVAILABLE:
        console.print("[warning]⚠ Planner module not fully integrated yet[/]")
        console.print("[info]Backend integration coming soon[/]")
        return
    
    # Step 2: Generate plan
    console.print("[info]🤖 Creating organization plan with AI...[/]")
    
    with console.status("[info]Thinking..."):
        try:
            planner = PlannerAgent()
            plan = planner.generate(scan_result, user_prompt=prompt if prompt else None)
        except Exception as e:
            console.print(f"[error]Error creating plan:[/] {e}")
            raise typer.Exit(1)
    
    # Step 3: Show preview
    console.print()
    try:
        preview = generate_terminal_preview(plan)
        console.print(preview)
    except Exception as e:
        console.print(f"[warning]Could not generate preview:[/] {e}")
        # Show basic info instead
        console.print(f"[info]Plan Summary:[/]")
        console.print(f"  Task ID: [highlight]{plan.task_id}[/]")
        console.print(f"  Actions: [count]{len(plan.actions)}[/count]")
    
    # Step 4: Show summary
    console.print(f"\n[success]✓ Plan created successfully[/]")
    console.print(f"  Task ID: [highlight]{plan.task_id}[/]")
    console.print(f"  Total actions: [count]{len(plan.actions)}[/count]")
    console.print(f"  Folders to create: [count]{len(plan.folders_to_create)}[/count]")
    
    # Count action types
    moves = sum(1 for a in plan.actions if a.type.value == "MOVE")
    renames = sum(1 for a in plan.actions if a.type.value == "RENAME")
    deletes = sum(1 for a in plan.actions if a.type.value == "DELETE")
    
    if moves:
        console.print(f"  • Moves: [count]{moves}[/count]")
    if renames:
        console.print(f"  • Renames: [count]{renames}[/count]")
    if deletes:
        console.print(f"  • Deletes: [warning]{deletes}[/warning]")
    
    if plan.ambiguous_files:
        console.print(f"  [warning]⚠ Ambiguous files: {len(plan.ambiguous_files)}[/]")
        console.print(f"    [muted](AI needs your help to decide what to do)[/muted]")
    
    # Next steps
    console.print(f"\n[highlight]Next steps:[/]")
    console.print(f"  • Review plan: [path]sentinel plan {path} --verbose[/path]")
    console.print(f"  • Execute plan: [path]sentinel apply {plan.task_id}[/path]")
    console.print(f"  • Modify plan: [muted](Manual editing coming soon)[/muted]")
