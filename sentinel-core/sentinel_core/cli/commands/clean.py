"""
Clean Command

Clean common directories (Downloads, Desktop, Documents).
"""

from pathlib import Path
from typing import List
import typer
from typing_extensions import Annotated

from sentinel_core.scanner import scan_directory
try:
    from sentinel_core.planner import PlannerAgent
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

from ..console import console


def clean_command(
    locations: Annotated[
        List[str],
        typer.Option(
            "--location", "-l",
            help="Locations to clean (Downloads, Desktop, Documents)"
        )
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run/--execute", help="Preview without executing")] = True,
):
    """
    Clean common directories (Downloads, Desktop, Documents).
    
    Scans and organizes your Downloads, Desktop, and Documents folders.
    By default runs in dry-run mode - use --execute to apply changes.
    """
    
    # Default locations
    if not locations:
        locations = ["Downloads", "Desktop", "Documents"]
    
    home = Path.home()
    paths_to_clean = []
    
    # Validate locations
    for loc in locations:
        path = home / loc
        if path.exists() and path.is_dir():
            paths_to_clean.append((loc, path))
        else:
            console.print(f"[warning]⚠ Skipping:[/] {loc} not found at {path}")
    
    if not paths_to_clean:
        console.print("[error]Error:[/] No valid locations found")
        console.print("\n[info]Available locations:[/]")
        console.print("  • Downloads")
        console.print("  • Desktop")
        console.print("  • Documents")
        console.print("\n[info]Usage:[/] sentinel clean-pc --location Downloads --location Desktop")
        raise typer.Exit(1)
    
    # Header
    console.print(f"[info]🧹 Cleaning {len(paths_to_clean)} locations...[/]\n")
    
    if dry_run:
        console.print("[highlight]Dry-run mode:[/] No changes will be made")
        console.print("[muted]Use --execute to apply changes[/]\n")
    
    # Process each location
    task_ids = []
    
    for loc_name, path in paths_to_clean:
        console.print(f"[highlight]📁 {loc_name}[/] ([path]{path}[/path])")
        
        # Scan
        with console.status(f"[info]Scanning {loc_name}..."):
            try:
                scan_result = scan_directory(str(path))
            except Exception as e:
                console.print(f"  [error]✗ Error:[/] {e}\n")
                continue
        
        if scan_result.total_files == 0:
            console.print(f"  [muted]Empty directory[/]\n")
            continue
        
        console.print(f"  Files: [count]{scan_result.total_files}[/count]")
        
        #        # Plan
        if not BACKEND_AVAILABLE:
            console.print(f"  [warning]⚠ Planner not available yet[/]\n")
            continue
        
        with console.status("Planning..."):
            try:
                planner = PlannerAgent()
                plan = planner.generate(
                    scan_result,
                    user_prompt="Organize and clean this directory"
                )
            except Exception as e:
                console.print(f"  [error]✗ Error:[/] {e}\n")
                continue
        
        console.print(f"  Actions: [count]{len(plan.actions)}[/count]")
        console.print(f"  Task ID: [highlight]{plan.task_id}[/]\n")
        
        task_ids.append(plan.task_id)
    
    # Summary
    if task_ids:
        console.print(f"[success]✓ Created {len(task_ids)} organization plans[/]\n")
        
        if dry_run:
            console.print("[highlight]Next steps:[/]")
            console.print("  Review and execute each plan:")
            for task_id in task_ids:
                console.print(f"    [path]sentinel apply {task_id}[/path]")
        else:
            console.print("[info]Plans executed successfully[/]")
            console.print("\n[highlight]To undo:[/]")
            for task_id in task_ids:
                console.print(f"  [path]sentinel undo {task_id}[/path]")
    else:
        console.print("[warning]No plans created[/]")
