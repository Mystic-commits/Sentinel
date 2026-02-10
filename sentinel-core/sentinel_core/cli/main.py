"""
Sentinel CLI - Main Application

Entry point for the Sentinel command-line interface.
"""

import typer
from typing_extensions import Annotated

from .console import console

# Create Typer app
app = typer.Typer(
    name="sentinel",
    help="🛡️  Sentinel - AI-powered file organization assistant",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """Display version and exit."""
    if value:
        console.print("[highlight]Sentinel[/] v0.1.0")
        console.print("[muted]Local-first AI file organizer[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
):
    """
    Sentinel - AI-powered file organization assistant.
    
    Safely organize your Downloads, Desktop, and Documents with AI assistance.
    All operations are logged and reversible.
    """
    pass


# Register commands
from .commands import scan, plan, apply, clean, undo, ask

app.command(name="scan")(scan.scan_command)
app.command(name="plan")(plan.plan_command)
app.command(name="apply")(apply.apply_command)
app.command(name="clean-pc")(clean.clean_command)
app.command(name="undo")(undo.undo_command)
app.command(name="ask")(ask.ask_command)


if __name__ == "__main__":
    app()
