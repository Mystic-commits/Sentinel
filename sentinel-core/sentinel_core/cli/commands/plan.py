"""Create and review a folder-scoped organization plan."""

import asyncio
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import typer
from rich.table import Table
from rich.text import Text

from sentinel_core.api.limits import MAX_MODEL_FILES, MAX_SCAN_ENTRIES, MAX_SCAN_SECONDS
from sentinel_core.cleanpc.pipeline import CleanPCPipeline
from sentinel_core.executor import Executor
from sentinel_core.models.planner import PlanSchema
from sentinel_core.planner.ollama_client import OllamaClient
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.safety import SafetyValidator

from ..console import console, watch_status
from ..saved_plans import save_plan


def show_plan(plan: PlanSchema, selected: set[int] | None = None) -> None:
    console.print(Text(f"Task {plan.task_id}"))
    console.print(Text(f"Folder {plan.scope_path}"))
    table = Table("Action", "Change", "From", "To")
    for index, action in enumerate(plan.actions, 1):
        if selected is None or index in selected:
            table.add_row(
                str(index),
                action.type.value,
                Text(action.source_path or ""),
                Text(action.destination_path or ""),
            )
    console.print(table)


def plan_command(
    path: Annotated[
        Path, typer.Argument(help="Folder to organize", exists=True, dir_okay=True, file_okay=False)
    ] = Path(),
    prompt: Annotated[
        str, typer.Option("--prompt", "-p", help="Instructions for the local AI")
    ] = "",
    save: Annotated[
        bool, typer.Option("--save/--no-save", help="Save the plan for later apply")
    ] = True,
    rules_only: Annotated[
        bool, typer.Option("--rules-only", help="Use local rules without Ollama")
    ] = False,
):
    """Review a proposed plan for a single folder."""
    if rules_only and prompt:
        raise typer.BadParameter("Custom instructions require local AI", param_hint="--prompt")
    if len(prompt) > 1000:
        raise typer.BadParameter("Use at most 1,000 characters", param_hint="--prompt")
    task_id = f"task-{uuid4()}"
    ollama = OllamaClient()
    try:
        planner = PlannerAgent(ollama, user_prompt=prompt)
        pipeline = CleanPCPipeline(planner, SafetyValidator(), Executor())
        with watch_status("[info]Preparing the file plan…[/]"):
            result = asyncio.run(
                pipeline.scan_and_plan(
                    task_id,
                    target_dirs=[str(path.resolve())],
                    scoped_moves_only=True,
                    max_entries=MAX_SCAN_ENTRIES,
                    max_scan_seconds=MAX_SCAN_SECONDS,
                    max_model_files=MAX_MODEL_FILES,
                    use_ai=not rules_only,
                )
            )
        plan = result["plan"]
        if result["summary"].get("truncated"):
            console.print("[warning]Partial scan. The plan covers only the files reached.[/]")
        console.print(Text(plan.summary))
        if not plan.actions:
            console.print("[warning]No moves or renames were proposed.[/]")
            return
        show_plan(plan)
        if save:
            save_plan(plan)
            console.print(f"Preview saved plan: sentinel apply {task_id} --dry-run")
    except Exception as error:
        console.print(Text(f"Could not create the plan: {error}", style="error"))
        raise typer.Exit(1) from error
    finally:
        ollama.close()
