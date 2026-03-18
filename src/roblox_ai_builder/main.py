"""CLI entry point for Roblox AI Builder."""

from __future__ import annotations

import asyncio
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.prompt import Prompt

from roblox_ai_builder.core.game_planner import GamePlanner
from roblox_ai_builder.core.models import Genre
from roblox_ai_builder.core.orchestrator import Orchestrator
from roblox_ai_builder.core.prompt_engine import PromptEngine
from roblox_ai_builder.generators.asset_guide import AssetGuide
from roblox_ai_builder.generators.luau_generator import LuauGenerator
from roblox_ai_builder.generators.system_presets import SystemPresets
from roblox_ai_builder.generators.ui_builder import UIBuilder
from roblox_ai_builder.output.history_manager import HistoryManager
from roblox_ai_builder.output.rojo_writer import RojoWriter
from roblox_ai_builder.utils.ai_client import AIClient
from roblox_ai_builder.utils.config import Config
from roblox_ai_builder.utils.errors import RABError
from roblox_ai_builder.utils.logger import (
    console,
    create_progress,
    print_error,
    print_game_plan,
    print_header,
    print_next_steps,
    print_output,
    print_success,
    print_warning,
)

app = typer.Typer(
    name="rab",
    help="Roblox AI Builder - Generate complete Roblox games from a single prompt",
    no_args_is_help=True,
)


def _run_async(coro):
    """Run async function in sync context."""
    return asyncio.run(coro)


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Game description prompt (any language)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Use local parsing only (no API calls)"),
    preview_only: bool = typer.Option(False, "--preview", "-p", help="Preview plan without generating"),
) -> None:
    """Generate a complete Roblox game project from a prompt."""
    print_header()
    config = Config.load()

    if output:
        config.output_dir = output

    # Setup AI client
    ai_client = None
    if not no_ai:
        errors = config.validate()
        if errors:
            for e in errors:
                print_warning(e)
            console.print("[dim]Falling back to local parsing (no AI)...[/dim]")
        else:
            ai_client = AIClient(api_key=config.api_key, model=config.model)

    try:
        result = _run_async(_generate_async(prompt, config, ai_client, preview_only))
        if result and not preview_only:
            print_success(f"Project generated at: {result}")
            print_next_steps(str(result))
    except RABError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(0)


async def _generate_async(
    prompt: str,
    config: Config,
    ai_client: AIClient | None,
    preview_only: bool,
) -> Path | None:
    """Async generation pipeline."""
    progress = create_progress()

    with progress:
        # Step 1: Parse prompt
        task_parse = progress.add_task("Analyzing prompt...", total=100)
        engine = PromptEngine(ai_client=ai_client)
        parsed = await engine.parse(prompt)
        progress.update(task_parse, completed=100)

        console.print(f"\n[cyan]Detected:[/cyan] {parsed.language.upper()}, Genre: {parsed.genre.value}")

        # Step 2: Create game plan
        task_plan = progress.add_task("Planning game structure...", total=100)
        planner = GamePlanner()
        plan = planner.plan(parsed)
        progress.update(task_plan, completed=100)

    # Show plan
    print_game_plan(
        genre=plan.genre.value,
        systems=[s.value for s in plan.systems],
        ui=[u.value for u in plan.ui_specs],
        scripts_count=len(plan.scripts),
    )

    if preview_only:
        console.print("\n[dim]Preview mode - no files generated[/dim]")
        return None

    # Step 3: Generate
    with progress:
        task_gen = progress.add_task("Generating game files...", total=100)

        presets = SystemPresets()
        ui_builder = UIBuilder(ai_client=ai_client)
        asset_guide = AssetGuide()
        luau_gen = LuauGenerator(ai_client) if ai_client else _create_fallback_luau_gen()

        orchestrator = Orchestrator(
            luau_gen=luau_gen,
            ui_builder=ui_builder,
            asset_guide=asset_guide,
            presets=presets,
        )

        project = await orchestrator.run_pipeline(plan)
        progress.update(task_gen, completed=100)

    # Step 4: Write output
    with progress:
        task_write = progress.add_task("Writing project files...", total=100)
        writer = RojoWriter()
        output_path = writer.write(project, config.output_dir)
        progress.update(task_write, completed=100)

    print_output(str(output_path), len(project.files))

    # Save to history
    try:
        hm = HistoryManager()
        hm.save(
            prompt=prompt,
            genre=plan.genre.value,
            game_name=plan.game_name,
            output_dir=str(output_path),
            file_count=len(project.files),
            systems=[s.value for s in plan.systems],
        )
    except Exception:
        pass  # History saving is non-critical

    return output_path


def _create_fallback_luau_gen() -> LuauGenerator:
    """Create a LuauGenerator with a dummy client for fallback-only mode."""
    # In no-ai mode, LuauGenerator will use its fallback scripts
    class DummyClient:
        async def generate_luau_scripts(self, *args, **kwargs):
            raise RABError("No AI client available")

    return LuauGenerator(DummyClient())  # type: ignore[arg-type]


@app.command()
def preview(
    prompt: str = typer.Argument(..., help="Game description prompt"),
) -> None:
    """Preview what would be generated without creating files."""
    generate(prompt=prompt, preview_only=True)


@app.command()
def presets(
    show: Optional[str] = typer.Argument(None, help="Show details for a specific preset"),
) -> None:
    """List available game presets."""
    print_header()
    sp = SystemPresets()
    available = sp.list_presets()

    if show:
        if show in available:
            console.print(Panel(f"[bold]{show}[/bold] preset", border_style="green"))
            preset_info = {
                "obby": "Obstacle course / Parkour game with checkpoints and leaderboard",
                "tycoon": "Business tycoon with droppers, conveyors, and upgrades",
                "simulator": "Simulator game with pets, zones, rebirths, and progression",
                "rpg": "RPG with quests, dialog, XP/leveling, and combat",
                "fps": "First-person shooter with weapons, raycasting, and K/D tracking",
                "survival": "Survival game with day/night, hunger/thirst, and wave defense",
                "horror": "Horror game with flashlight, sanity, keys, and dark atmosphere",
                "racing": "Racing game with laps, checkpoints, vehicles, and timing",
            }
            console.print(preset_info.get(show, "Custom preset"))
        else:
            print_error(f"Preset '{show}' not found. Available: {', '.join(available)}")
    else:
        console.print("[bold]Available Presets:[/bold]\n")
        genre_map = {
            "obby": ("Obstacle Course", Genre.OBBY),
            "tycoon": ("Tycoon", Genre.TYCOON),
            "simulator": ("Simulator", Genre.SIMULATOR),
            "rpg": ("RPG Adventure", Genre.RPG),
            "fps": ("FPS / Shooter", Genre.FPS),
            "survival": ("Survival", Genre.SURVIVAL),
            "horror": ("Horror", Genre.HORROR),
            "racing": ("Racing", Genre.RACING),
        }
        for preset_id in available:
            name, _ = genre_map.get(preset_id, (preset_id, Genre.CUSTOM))
            console.print(f"  [green]{preset_id:12}[/green] {name}")


@app.command()
def login() -> None:
    """Authenticate with Anthropic API via browser + CLI key input."""
    print_header()
    console.print(
        Panel(
            "[bold]Anthropic API Key Setup[/bold]\n\n"
            "1. Browser will open to Anthropic Console (API Keys page)\n"
            "2. Create or copy your API key\n"
            "3. Paste it here\n\n"
            "[dim]Your key is stored locally at ~/.config/roblox-ai-builder/config.toml[/dim]",
            border_style="cyan",
        )
    )

    open_browser = Prompt.ask(
        "Open Anthropic Console in browser?", choices=["y", "n"], default="y"
    )
    if open_browser == "y":
        webbrowser.open("https://console.anthropic.com/settings/keys")
        console.print("[dim]Browser opened. Copy your API key...[/dim]\n")

    api_key = Prompt.ask("Paste your API key (sk-ant-...)")
    if not api_key.startswith("sk-ant-"):
        print_warning("Key doesn't look like an Anthropic key (expected sk-ant-...). Saving anyway.")

    # Verify the key works
    console.print("[dim]Verifying key...[/dim]")
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "hi"}],
        )
        print_success("API key verified!")
    except Exception as e:
        print_warning(f"Could not verify key: {e}")
        console.print("[dim]Saving anyway — you can test later with `rab generate --preview`[/dim]")

    # Save to config
    config = Config.load()
    config.api_key = api_key
    config.save()
    from roblox_ai_builder.utils.config import DEFAULT_CONFIG_PATH
    print_success(f"Key saved to {DEFAULT_CONFIG_PATH}")
    console.print("\n[bold]Ready![/bold] Try: [cyan]rab generate \"좀비 서바이벌 게임 만들어줘\"[/cyan]")


@app.command(name="config")
def config_cmd(
    action: str = typer.Argument(..., help="Action: set, show"),
    key: Optional[str] = typer.Argument(None, help="Config key (for 'set')"),
    value: Optional[str] = typer.Argument(None, help="Config value (for 'set')"),
) -> None:
    """Manage configuration."""
    config = Config.load()

    if action == "show":
        console.print("[bold]Current Configuration:[/bold]\n")
        console.print(f"  API Key: {'***' + config.api_key[-4:] if config.api_key else '[red]NOT SET[/red]'}")
        console.print(f"  Model:   {config.model}")
        console.print(f"  Output:  {config.output_dir}")
    elif action == "set":
        if not key or not value:
            print_error("Usage: rab config set <key> <value>")
            raise typer.Exit(1)
        if key == "api-key":
            config.api_key = value
        elif key == "model":
            config.model = value
        elif key == "output":
            config.output_dir = Path(value)
        else:
            print_error(f"Unknown config key: {key}")
            raise typer.Exit(1)
        config.save()
        print_success(f"Set {key} = {'***' if key == 'api-key' else value}")
    else:
        print_error(f"Unknown action: {action}. Use 'set' or 'show'")


@app.command()
def history(
    record_id: Optional[str] = typer.Argument(None, help="Record ID to show details"),
) -> None:
    """View generation history."""
    print_header()
    hm = HistoryManager()
    records = hm.list_records()

    if record_id:
        record = hm.get_record(record_id)
        if record:
            console.print(Panel(f"[bold]{record['game_name']}[/bold]", border_style="green"))
            console.print(f"  ID:       {record['id']}")
            console.print(f"  Genre:    {record['genre']}")
            console.print(f"  Prompt:   {record['prompt']}")
            console.print(f"  Output:   {record['output_dir']}")
            console.print(f"  Files:    {record['file_count']}")
            console.print(f"  Systems:  {', '.join(record.get('systems', []))}")
            console.print(f"  Time:     {record['timestamp']}")
        else:
            print_error(f"Record '{record_id}' not found")
    elif records:
        console.print("[bold]Generation History:[/bold]\n")
        for r in records[-10:]:  # Show last 10
            console.print(
                f"  [green]{r['id']}[/green]  {r['game_name']:20}  "
                f"{r['genre']:12}  {r['timestamp'][:10]}"
            )
    else:
        console.print("[dim]No generation history yet.[/dim]")


if __name__ == "__main__":
    app()
