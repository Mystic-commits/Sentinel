"""
Ask Command

Ask AI questions about files.
"""

import typer
from pathlib import Path
from typing_extensions import Annotated
from rich.panel import Panel
from rich.markdown import Markdown

from sentinel_core.planner.ollama_client import OllamaClient
from ..console import console


def ask_command(
    question: Annotated[str, typer.Argument(help="Question to ask the AI")],
    context_path: Annotated[
        Path,
        typer.Option("--path", "-p", help="Path for context")
    ] = Path("."),
):
    """
    Ask AI a question about your files.
    
    Get AI-powered insights about file organization, storage usage,
    and recommendations for cleaning up your system.
    """
    
    # Display question
    console.print(f"[info]❓ Question:[/] {question}\n")
    
    # Validate context path if provided
    if context_path != Path(".") and not context_path.exists():
        console.print(f"[warning]Warning:[/] Context path not found: {context_path}")
        console.print("[muted]Proceeding without file context...[/]\n")
        context_path = None
    
    # Get AI response
    with console.status("[info]🤖 Thinking..."):
        try:
            client = OllamaClient()
            
            # Build context
            context = None
            if context_path and context_path.exists():
                # Could scan the path and provide file statistics
                # For now, just use the path
                context = f"User is asking about files in: {context_path.absolute()}"
            
            # Get response
            response = client.chat(
                question,
                context=context
            )
            
        except Exception as e:
            console.print(f"[error]Error communicating with AI:[/] {e}")
            console.print("\n[info]Tips:[/]")
            console.print("  • Make sure Ollama is running")
            console.print("  • Check model is available: [path]ollama list[/path]")
            console.print("  • Start Ollama: [path]ollama serve[/path]")
            raise typer.Exit(1)
    
    # Display response
    console.print()
    
    try:
        # Try to render as markdown
        md = Markdown(response)
        console.print(
            Panel(
                md,
                title="[bold cyan]🤖 AI Response[/]",
                border_style="cyan",
                padding=(1, 2)
            )
        )
    except Exception:
        # Fallback to plain text
        console.print(
            Panel(
                response,
                title="[bold cyan]🤖 AI Response[/]",
                border_style="cyan",
                padding=(1, 2)
            )
        )
    
    # Suggestions
    console.print(f"\n[highlight]Follow-up actions:[/]")
    console.print(f"  • Scan files: [path]sentinel scan {context_path or '.'}[/path]")
    console.print(f"  • Create plan: [path]sentinel plan {context_path or '.'}[/path]")
    console.print(f"  • Ask more: [path]sentinel ask \"<your question>\"[/path]")
