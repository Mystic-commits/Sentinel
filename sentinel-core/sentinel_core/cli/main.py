"""Command-line access to the same persisted workflow as the dashboard."""

import argparse
from pathlib import Path

import httpx
from rich.console import Console

from .shell import Shell, main as interactive


def app(argv=None):
    parser = argparse.ArgumentParser(description="Sentinel local file organizer")
    parser.add_argument("--version", action="version", version="Sentinel 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("shell", help="Open the interactive prompt")
    scan = commands.add_parser("scan", help="Read-only folder scan")
    scan.add_argument("path", type=Path)
    plan = commands.add_parser("plan", help="Create a persisted preview; never execute")
    plan.add_argument("path", type=Path)
    plan.add_argument("--prompt", default="Organize by file type. Do not delete anything.")
    plan.add_argument("--strategy", choices=["local_ai", "file_types"], default="local_ai")
    commands.add_parser("history", help="List persisted sessions")
    for name in ["status", "review", "apply"]:
        sub = commands.add_parser(name)
        sub.add_argument("task_id")
        if name == "apply":
            sub.add_argument("--actions", required=True, help="Original review numbers, e.g. 1,3")
    args = parser.parse_args(argv)
    if args.command == "shell":
        return interactive([])
    console = Console()
    try:
        if args.command == "scan":
            from sentinel_core.scanner import scan_directory

            path = args.path.expanduser().resolve()
            if not path.is_dir():
                raise ValueError("Choose an existing folder.")
            result = scan_directory(str(path))
            console.print(
                f"{len(result.files)} files, {sum(f.size_bytes for f in result.files)} bytes",
                markup=False,
            )
            for error in result.errors:
                console.print(str(error), markup=False)
            return
        with httpx.Client(base_url="http://127.0.0.1:8000", timeout=30, trust_env=False) as client:
            shell = Shell(client, console)
            if args.command == "plan":
                path = args.path.expanduser().resolve()
                if not path.is_dir():
                    raise ValueError("Choose an existing folder.")
                if not args.prompt.strip() or args.prompt.lstrip().startswith("/"):
                    raise ValueError("The plan prompt must be a description, not a shell command.")
                shell.path = str(path)
                shell.strategy = args.strategy
                shell.handle(args.prompt)
            elif args.command == "history":
                shell.handle("/history")
            else:
                shell.task_id = args.task_id
                shell.handle(
                    "/apply " + args.actions if args.command == "apply" else "/" + args.command
                )
    except (ValueError, httpx.HTTPError) as error:
        console.print(f"Could not continue: {error}", markup=False)
        raise SystemExit(1) from error
    except (EOFError, KeyboardInterrupt):
        console.print("Cancelled. No further changes requested.")
        raise SystemExit(1)


if __name__ == "__main__":
    app()
