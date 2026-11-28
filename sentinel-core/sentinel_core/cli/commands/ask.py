"""
Ask Command

Ask AI questions about files.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.markdown import Markdown
from rich.panel import Panel

from sentinel_core.planner.ollama_client import OllamaClient

from ..console import console, watch_status


def ask_command(
    question: Annotated[str, typer.Argument(help="Question to ask the AI")],
    context_path: Annotated[Path, typer.Option("--path", "-p", help="Path for context")] = Path(),
):
    """
    Ask AI a question about your files.

    Get AI-powered insights about file organization, storage usage,
    and recommendations for cleaning up your system.
    """

    # Display question
    console.print(f"[info]❓ Question:[/] {question}\n")

    # Validate context path if provided
    if context_path != Path() and not context_path.exists():
        console.print(f"[warning]Warning:[/] Context path not found: {context_path}")
        console.print("[muted]Proceeding without file context...[/]\n")
        context_path = None

    # Get AI response
    with watch_status("[info]🤖 Thinking..."):
        client = OllamaClient()
        try:

            # Build context
            context = None
            if context_path and context_path.exists():
                # Could scan the path and provide file statistics
                # For now, just use the path
                context = f"User is asking about files in: {context_path.absolute()}"

            # Get response
            response = client.generate(
                f"{context}\n\n{question}" if context else question, model="llama2"
            )

        except Exception as e:
            console.print(f"[error]Error communicating with AI:[/] {e}")
            console.print("\n[info]Tips:[/]")
            console.print("  • Make sure Ollama is running")
            console.print("  • Check model is available: [path]ollama list[/path]")
            console.print("  • Start Ollama: [path]ollama serve[/path]")
            raise typer.Exit(1) from e
        finally:
            client.close()

    # Display response
    console.print()

    try:
        # Try to render as markdown
        md = Markdown(response)
        console.print(
            Panel(md, title="[bold cyan]🤖 AI Response[/]", border_style="cyan", padding=(1, 2))
        )
    except Exception:
        # Fallback to plain text
        console.print(
            Panel(
                response, title="[bold cyan]🤖 AI Response[/]", border_style="cyan", padding=(1, 2)
            )
        )

    # Suggestions
    console.print("\n[highlight]Follow-up actions:[/]")
    console.print(f"  • Scan files: [path]sentinel scan {context_path or '.'}[/path]")
    console.print(f"  • Create plan: [path]sentinel plan {context_path or '.'}[/path]")
    console.print('  • Ask more: [path]sentinel ask "<your question>"[/path]')
