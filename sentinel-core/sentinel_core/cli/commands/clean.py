"""
Clean Command

Clean common directories (Downloads, Desktop, Documents).
"""

from pathlib import Path
from typing import Annotated, Optional

import typer

from ..console import console
from .apply import apply_command
from .plan import plan_command


def clean_command(
    locations: Annotated[
        Optional[list[str]],  # noqa: UP045 - Typer requires typing.Optional here
        typer.Option("--location", "-l", help="Locations to clean (Downloads, Desktop, Documents)"),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run/--execute", help="Preview without executing")
    ] = True,
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

    for _, path in paths_to_clean:
        task_id = plan_command(path=path, rules_only=True)
        if task_id and not dry_run:
            apply_command(task_id)
