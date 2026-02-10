"""
Clean My PC CLI Command

Typer command for running the Clean My PC pipeline.
"""

import typer
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from sentinel_core.cleanpc.pipeline import CleanPCPipeline
from sentinel_core.planner.planner_agent import PlannerAgent
from sentinel_core.planner.ollama_client import OllamaClient
from sentinel_core.safety.safety import SafetyValidator
from sentinel_core.executor import Executor

console = Console()
app = typer.Typer(help="Clean My PC - Intelligent file cleanup")


@app.command()
def scan(
    dirs: list[str] = typer.Option(
        None,
        "--dirs",
        "-d",
        help="Directories to scan (default: Downloads, Desktop, Documents, Videos)"
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Dry run mode (default: True)"
    ),
    max_depth: int = typer.Option(
        3,
        "--max-depth",
        "-m",
        help="Maximum directory depth to scan"
    ),
):
    """
    Scan directories and generate a cleanup plan.
    
    Examples:
        sentinel clean-pc scan
        sentinel clean-pc scan --dirs ~/Downloads ~/Desktop
        sentinel clean-pc scan --execute
    """
    console.print("\n[bold cyan]🧹 Clean My PC - Intelligent File Cleanup[/bold cyan]\n")
    
    # Initialize pipeline
    ollama_client = OllamaClient()
    planner = PlannerAgent(ollama_client)
    safety = SafetyValidator()
    executor = Executor()
    pipeline = CleanPCPipeline(planner=planner, safety=safety, executor=executor)
    
    # Generate task ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # Run pipeline
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task(description="Scanning directories...", total=None)
        
        try:
            # Run async pipeline
            result = asyncio.run(pipeline.scan_and_plan(
                task_id=task_id,
                target_dirs=dirs,
                max_depth=max_depth
            ))
        except Exception as e:
            console.print(f"[bold red]❌ Scan failed:[/bold red] {e}")
            raise typer.Exit(1)
    
    # Display summary
    summary = result["summary"]
    
    summary_table = Table(title="Scan Summary", show_header=False)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Files", str(summary["total_files"]))
    summary_table.add_row("Proposed Operations", str(summary["operations"]))
    summary_table.add_row("Old Installers", str(summary["installers_found"]))
    summary_table.add_row("Archives", str(summary["archives_found"]))
    summary_table.add_row("Large Videos", str(summary["large_videos"]))
    summary_table.add_row("Screenshots", str(summary["screenshots"]))
    summary_table.add_row("Duplicates", str(summary["duplicates"]))
    summary_table.add_row("Total Size", f"{summary['total_size_mb']} MB")
    
    console.print(summary_table)
    
    # Display warnings if any
    if result["validation"]["warnings"]:
        console.print("\n[bold yellow]⚠️  Warnings:[/bold yellow]")
        for warning in result["validation"]["warnings"]:
            console.print(f"  • {warning}")
    
    # Display operations
    plan = result["plan"]
    
    if plan.actions:
        console.print(f"\n[bold]📋 Proposed Operations ({len(plan.actions)}):[/bold]\n")
        
        ops_table = Table(show_header=True, header_style="bold magenta")
        ops_table.add_column("Action", style="yellow")
        ops_table.add_column("File", style="cyan", no_wrap=False)
        ops_table.add_column("Target", style="green")
        ops_table.add_column("Reason", style="white", no_wrap=False)
        
        # Show first 20 operations
        for op in plan.actions[:20]:
            action = op.type.value.upper()
            file_name = Path(op.source_path).name
            target = op.destination_path or "Trash"
            reason = op.reason[:60] + "..." if len(op.reason) > 60 else op.reason
            
            ops_table.add_row(action, file_name, target, reason)
        
        if len(plan.actions) > 20:
            ops_table.add_row("...", f"({len(plan.actions) - 20} more)", "...", "...")
        
        console.print(ops_table)
    else:
        console.print("\n[green]✅ No cleanup needed! Everything looks good.[/green]")
    
    # Execution
    if not dry_run and plan.actions:
        console.print(f"\n[bold red]⚠️  EXECUTION MODE - Changes will be made![/bold red]")
        
        if not typer.confirm("\nProceed with execution?"):
            console.print("[yellow]Execution cancelled.[/yellow]")
            raise typer.Exit(0)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(description="Executing operations...", total=None)
            
            exec_result = asyncio.run(pipeline.execute_plan(
                task_id=task_id,
                plan=plan,
                dry_run=False
            ))
        
        console.print(f"\n[bold green]✅ Execution complete![/bold green]")
        console.print(f"  • Success: {exec_result['success_count']}")
        console.print(f"  • Failed: {exec_result['failure_count']}")
        
        if exec_result['errors']:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in exec_result['errors'][:10]:
                console.print(f"  • {error}")
    
    elif dry_run:
        console.print("\n[dim]💡 This was a dry run. Use --execute to apply changes.[/dim]")
    
    console.print()


if __name__ == "__main__":
    app()
