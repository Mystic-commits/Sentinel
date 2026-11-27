"""Review and apply selected actions from a saved plan."""

import sqlite3
from typing import Annotated, Optional

import typer
from rich.text import Text

from sentinel_core.api.config import settings
from sentinel_core.api.file_jobs import run_file_job_sync
from sentinel_core.api.mutation_jobs import (
    MUTATION_TIMEOUT,
    PREFLIGHT_TIMEOUT,
    apply_moves,
    prepare_apply,
)
from sentinel_core.models.enums import ActionType
from sentinel_core.models.executor import ExecutionResult

from ..console import console, watch_status
from ..saved_plans import load_plan
from ..ui.prompts import confirm
from .plan import show_plan


def apply_command(
    task_id: Annotated[str, typer.Argument(help="Saved task ID")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Apply the reviewed selection without prompting")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Review without making changes")
    ] = False,
    action: Annotated[
        Optional[list[int]],  # noqa: UP045 - Typer requires typing.Optional here
        typer.Option("--action", help="Action number to approve. Repeat to approve several."),
    ] = None,
):
    """Apply saved moves and renames with a durable undo receipt."""
    try:
        stored = load_plan(task_id)
        if stored is None:
            raise ValueError("Saved plan not found. Create one with sentinel plan.")
        plan, snapshot = stored
        selected = set(action or range(1, len(plan.actions) + 1))
        if not selected or min(selected) < 1 or max(selected) > len(plan.actions):
            raise ValueError("Select valid action numbers from the plan")
        approved = plan.model_copy(
            update={
                "actions": [plan.actions[index - 1] for index in sorted(selected)],
                "folders_to_create": [],
            }
        )
        if any(item.type not in (ActionType.MOVE, ActionType.RENAME) for item in approved.actions):
            raise ValueError("The CLI preview supports moves and renames")
        show_plan(plan, selected)
        if not dry_run and not yes and not confirm(f"Apply {len(selected)} approved changes?"):
            console.print("[warning]Cancelled.[/]")
            return
        preflight = run_file_job_sync(
            prepare_apply,
            approved,
            snapshot,
            plan.scope_path,
            settings.database_url,
            not dry_run,
            timeout=PREFLIGHT_TIMEOUT,
        )
        if "error" in preflight:
            raise ValueError(preflight["error"])
        if dry_run:
            console.print("[info]Dry run. No files moved.[/]")
            return
        with watch_status("[info]Applying approved changes…[/]"):
            result = ExecutionResult.model_validate(
                run_file_job_sync(
                    apply_moves,
                    approved,
                    snapshot,
                    settings.database_url,
                    timeout=MUTATION_TIMEOUT,
                )
            )
        if result.failed_actions or result.error_message:
            raise ValueError(result.error_message or "One or more changes failed")
    except TimeoutError as error:
        console.print("[error]Apply timed out. Check the execution receipt before retrying.[/]")
        raise typer.Exit(1) from error
    except (ValueError, OSError, RuntimeError, sqlite3.Error) as error:
        console.print(Text(str(error), style="error"))
        raise typer.Exit(1) from error
    console.print(f"[success]Applied {result.successful_actions} changes.[/]")
    console.print(f"Restore eligible files: sentinel undo {task_id}")
