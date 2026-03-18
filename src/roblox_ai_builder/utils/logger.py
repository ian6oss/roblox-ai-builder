"""Rich-based logging and terminal output for Roblox AI Builder."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.tree import Tree

console = Console()


def print_header() -> None:
    """Print application header."""
    console.print(
        Panel(
            "[bold cyan]Roblox AI Builder[/bold cyan] v0.1.0\n"
            "[dim]Generate complete Roblox games from a single prompt[/dim]",
            border_style="cyan",
        )
    )


def print_game_plan(genre: str, systems: list[str], ui: list[str], scripts_count: int) -> None:
    """Print the game plan tree."""
    tree = Tree("[bold green]Game Plan")
    tree.add(f"[yellow]Genre:[/yellow] {genre}")

    systems_branch = tree.add("[yellow]Systems")
    for s in systems:
        systems_branch.add(s)

    ui_branch = tree.add("[yellow]UI Components")
    for u in ui:
        ui_branch.add(u)

    tree.add(f"[yellow]Estimated files:[/yellow] {scripts_count}")
    console.print(tree)


def print_output(output_dir: str, file_count: int) -> None:
    """Print output summary."""
    table = Table(title="Generated Project", show_header=False, border_style="green")
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_row("Output", output_dir)
    table.add_row("Files", str(file_count))
    console.print(table)


def create_progress() -> Progress:
    """Create a Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_next_steps(output_dir: str) -> None:
    """Print next steps after generation."""
    console.print(
        Panel(
            f"[bold]Next steps:[/bold]\n"
            f"  1. cd {output_dir}\n"
            f"  2. rojo serve    [dim](if Rojo is installed)[/dim]\n"
            f"  3. Connect from Roblox Studio or import files manually\n"
            f"  4. Check ASSET_GUIDE.md for asset placement instructions",
            title="What's Next",
            border_style="blue",
        )
    )
