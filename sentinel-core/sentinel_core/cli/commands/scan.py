"""
Scan Command

Scan a directory and display file statistics.
"""

from pathlib import Path
import typer
from rich.table import Table
from typing_extensions import Annotated

from sentinel_core.scanner import scan_directory
from ..console import console


def _format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def scan_command(
    path: Annotated[Path, typer.Argument(help="Path to scan", exists=True)] = Path("."),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed output")] = False,
):
    """
    Scan a directory and show file statistics.
    
    Analyzes files by type, size, and other metadata without making any changes.
    """
    
    # Validate path
    if not path.exists():
        console.print(f"[error]Error:[/] Path not found: {path}")
        raise typer.Exit(1)
    
    if not path.is_dir():
        console.print(f"[error]Error:[/] Not a directory: {path}")
        raise typer.Exit(1)
    
    # Perform scan
    console.print(f"[info]Scanning:[/] [path]{path.absolute()}[/path]")
    
    with console.status("[info]Analyzing files..."):
        try:
            result = scan_directory(str(path.absolute()))
        except Exception as e:
            console.print(f"[error]Error during scan:[/] {e}")
            raise typer.Exit(1)
    
    # Display summary
    console.print(f"\n[success]✓ Scan complete[/]")
    
    total_files = len(result.files)
    total_size = sum(f.size_bytes for f in result.files)
    scan_duration = (result.scanned_at - result.scanned_at).total_seconds() if hasattr(result, 'scan_duration_seconds') else 0.0
    
    console.print(f"  Total files: [count]{total_files}[/count]")
    console.print(f"  Total size: [count]{_format_size(total_size)}[/count]")
    
    if result.errors:
        console.print(f"  [warning]Errors: {len(result.errors)}[/warning]")
    
    if total_files == 0:
        console.print("\n[warning]No files found in this directory[/]")
        return
    
    # Compute file type breakdown
    file_types = {}
    size_by_type = {}
    
    for file in result.files:
        ext = file.extension if file.extension else "(no extension)"
        file_types[ext] = file_types.get(ext, 0) + 1
        size_by_type[ext] = size_by_type.get(ext, 0) + file.size_bytes
    
    # Show file type breakdown
    console.print()
    table = Table(
        title="📁 File Type Breakdown",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Extension", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="count")
    table.add_column("Total Size", justify="right")
    table.add_column("% of Total", justify="right", style="muted")
    
    # Sort by file count descending
    sorted_types = sorted(
        file_types.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Show top 20 file types
    for ext, count in sorted_types[:20]:
        size = size_by_type.get(ext, 0)
        percentage = (size / total_size * 100) if total_size > 0 else 0
        
        ext_display = ext if ext else "(no extension)"
        table.add_row(
            ext_display,
            str(count),
            _format_size(size),
            f"{percentage:.1f}%"
        )
    
    if len(sorted_types) > 20:
        table.add_row(
            "[muted]...[/muted]",
            f"[muted]{sum(c for _, c in sorted_types[20:])}[/muted]",
            "[muted]...[/muted]",
            "[muted]...[/muted]"
        )
    
    console.print(table)
    
    # Verbose output
    if verbose:
        console.print("\n[highlight]Top 10 Largest Files:[/]")
        
        # This would require file-level data from scanner
        # For now, just show a placeholder
        console.print("[muted]  (File-level details coming soon)[/muted]")
    
    console.print(f"\n[highlight]Next steps:[/]")
    console.print(f"  • Create organization plan: [path]sentinel plan {path}[/path]")
    console.print(f"  • Ask AI for help: [path]sentinel ask \"What should I do with these files?\"[/path]")
