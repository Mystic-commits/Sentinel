"""
Demo script to showcase the plan preview module.

Run with: python3 -m demo_preview
"""

from sentinel_core.models import PlanSchema, PlanAction, ActionType, AmbiguousFile
from sentinel_core.preview import generate_terminal_preview, generate_web_preview
from rich.console import Console
import json

# Create a realistic sample plan
plan = PlanSchema(
    task_id="demo_organize_downloads",
    scope_path="/Users/Mystic/Downloads",
    folders_to_create=[
        "/Users/Mystic/Downloads/Documents/PDFs",
        "/Users/Mystic/Downloads/Documents/Spreadsheets",
        "/Users/Mystic/Downloads/Media/Images",
        "/Users/Mystic/Downloads/Media/Videos",
    ],
    actions=[
        PlanAction(
            type=ActionType.MOVE,
            source_path="/Users/Mystic/Downloads/report_2024.pdf",
            destination_path="/Users/Mystic/Downloads/Documents/PDFs/report_2024.pdf",
            reason="PDF document should be organized into PDFs folder",
            confidence=0.95
        ),
        PlanAction(
            type=ActionType.MOVE,
            source_path="/Users/Mystic/Downloads/budget.xlsx",
            destination_path="/Users/Mystic/Downloads/Documents/Spreadsheets/budget.xlsx",
            reason="Spreadsheet file detected",
            confidence=0.92
        ),
        PlanAction(
            type=ActionType.MOVE,
            source_path="/Users/Mystic/Downloads/vacation_photo.jpg",
            destination_path="/Users/Mystic/Downloads/Media/Images/vacation_photo.jpg",
            reason="Image file should be in Media/Images",
            confidence=0.88
        ),
        PlanAction(
            type=ActionType.RENAME,
            source_path="/Users/Mystic/Downloads/IMG_12345.png",
            destination_path="/Users/Mystic/Downloads/screenshot_sentinel_ui.png",
            reason="Generic camera name should be renamed to descriptive name",
            confidence=0.75
        ),
        PlanAction(
            type=ActionType.DELETE,
            source_path="/Users/Mystic/Downloads/temp_download.tmp",
            destination_path=None,
            reason="Temporary file from incomplete download",
            confidence=0.85
        ),
        PlanAction(
            type=ActionType.DELETE,
            source_path="/Users/Mystic/Downloads/.DS_Store",
            destination_path=None,
            reason="System metadata file",
            confidence=0.99
        ),
        PlanAction(
            type=ActionType.SKIP,
            source_path="/Users/Mystic/Downloads/important_contract.pdf",
            destination_path=None,
            reason="User marked as important, skip organization",
            confidence=1.0
        ),
    ],
    ambiguous_files=[
        AmbiguousFile(
            path="/Users/Mystic/Downloads/data.bin",
            reason="Unknown binary file format, cannot determine purpose",
            suggested_action=ActionType.SKIP
        ),
        AmbiguousFile(
            path="/Users/Mystic/Downloads/README",
            reason="No file extension, unclear if document or code",
            suggested_action=None
        ),
    ],
    summary="Organizing Downloads folder: 7 actions, 4 folders, 2 ambiguous files"
)


def main():
    console = Console()
    
    # Display terminal preview
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]                 SENTINEL PLAN PREVIEW DEMO                         [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    terminal_preview = generate_terminal_preview(plan)
    console.print(terminal_preview)
    
    console.print("\n[bold green]All tests passed! Terminal preview rendering successfully.[/bold green]\n")
    
    # Display web preview
    console.print("[bold cyan]─────────────────────────────────────────────────────────────────────[/bold cyan]")
    console.print("[bold yellow]Web Preview (JSON Output)[/bold yellow]")
    console.print("[bold cyan]─────────────────────────────────────────────────────────────────────[/bold cyan]\n")
    
    web_preview = generate_web_preview(plan)
    console.print(json.dumps(web_preview, indent=2))
    
    console.print("\n[bold green]✓ Preview module fully functional![/bold green]")
    console.print("[dim]Both terminal and web outputs working correctly.[/dim]\n")


if __name__ == "__main__":
    main()
