"""Game planner - converts parsed prompts into executable generation plans."""

from __future__ import annotations

from pathlib import Path

from roblox_ai_builder.core.models import (
    GamePlan,
    Genre,
    ParsedPrompt,
    ScriptSpec,
    ScriptType,
    SystemType,
    UIType,
)


# Default systems per genre
GENRE_DEFAULT_SYSTEMS: dict[Genre, list[SystemType]] = {
    Genre.OBBY: [SystemType.CHECKPOINT, SystemType.LEADERBOARD],
    Genre.TYCOON: [SystemType.TYCOON_CORE, SystemType.ECONOMY],
    Genre.SIMULATOR: [SystemType.ECONOMY, SystemType.PET, SystemType.LEADERBOARD],
    Genre.RPG: [SystemType.INVENTORY, SystemType.COMBAT, SystemType.QUEST, SystemType.DIALOG],
    Genre.FPS: [SystemType.COMBAT, SystemType.LEADERBOARD],
    Genre.SURVIVAL: [SystemType.COMBAT, SystemType.INVENTORY, SystemType.WAVE_SPAWNER],
    Genre.HORROR: [SystemType.INVENTORY, SystemType.DIALOG],
    Genre.RACING: [SystemType.CHECKPOINT, SystemType.LEADERBOARD],
    Genre.CUSTOM: [],
}

# Genre to closest preset mapping
GENRE_PRESET_MAP: dict[Genre, str] = {
    Genre.OBBY: "obby",
    Genre.TYCOON: "tycoon",
    Genre.SIMULATOR: "simulator",
    Genre.RPG: "rpg",
    Genre.FPS: "fps",
    Genre.SURVIVAL: "survival",
    Genre.HORROR: "horror",
    Genre.RACING: "racing",
    Genre.CUSTOM: "obby",
}

# System to script assignments
SYSTEM_SERVER_SCRIPTS: dict[SystemType, list[str]] = {
    SystemType.INVENTORY: ["InventoryService"],
    SystemType.COMBAT: ["CombatService"],
    SystemType.SHOP: ["ShopService"],
    SystemType.LEADERBOARD: ["LeaderboardService"],
    SystemType.WAVE_SPAWNER: ["WaveManager"],
    SystemType.ECONOMY: ["EconomyService"],
    SystemType.CRAFTING: ["CraftingService"],
    SystemType.QUEST: ["QuestService"],
    SystemType.DIALOG: ["DialogService"],
    SystemType.GAMEPASS: ["GamePassService"],
    SystemType.DEV_PRODUCT: ["DevProductService"],
    SystemType.CHECKPOINT: ["CheckpointService"],
    SystemType.TYCOON_CORE: ["TycoonService"],
    SystemType.PET: ["PetService"],
    SystemType.TRADING: ["TradingService"],
}


class GamePlanner:
    """Converts ParsedPrompt into an executable GamePlan."""

    def __init__(self, presets_dir: Path | None = None):
        self.presets_dir = presets_dir

    def plan(self, parsed: ParsedPrompt) -> GamePlan:
        """Create a complete game plan from parsed prompt."""
        # Merge genre defaults with user-requested systems
        systems = self._merge_systems(parsed.genre, parsed.systems)

        # Select preset
        preset_id = GENRE_PRESET_MAP.get(parsed.genre, "obby")

        # Generate script specs
        scripts = self._generate_scripts(systems, parsed.genre)

        # Determine UI components
        ui_specs = parsed.ui_requests if parsed.ui_requests else [UIType.HUD]

        return GamePlan(
            genre=parsed.genre,
            preset_id=preset_id,
            game_name=parsed.game_name,
            scripts=scripts,
            ui_specs=ui_specs,
            systems=systems,
            asset_hints=parsed.asset_hints,
            custom_params=parsed.custom_params,
        )

    def _merge_systems(
        self, genre: Genre, requested: list[SystemType]
    ) -> list[SystemType]:
        """Merge genre default systems with user-requested ones."""
        defaults = GENRE_DEFAULT_SYSTEMS.get(genre, [])
        merged = list(defaults)
        for system in requested:
            if system not in merged:
                merged.append(system)
        return merged

    def _generate_scripts(
        self, systems: list[SystemType], genre: Genre
    ) -> list[ScriptSpec]:
        """Generate script specifications from systems list."""
        scripts: list[ScriptSpec] = []

        # Always add GameManager server script
        scripts.append(
            ScriptSpec(
                name="GameManager",
                script_type=ScriptType.SERVER,
                description="Main game loop and initialization",
                dependencies=[],
                systems=systems,
            )
        )

        # Add system-specific server scripts
        for system in systems:
            service_names = SYSTEM_SERVER_SCRIPTS.get(system, [])
            for name in service_names:
                scripts.append(
                    ScriptSpec(
                        name=name,
                        script_type=ScriptType.SERVER,
                        description=f"Server-side {system.value} logic",
                        dependencies=[],
                        systems=[system],
                    )
                )

        # Client scripts
        scripts.append(
            ScriptSpec(
                name="InputHandler",
                script_type=ScriptType.CLIENT,
                description="Player input handling",
            )
        )
        scripts.append(
            ScriptSpec(
                name="UIController",
                script_type=ScriptType.CLIENT,
                description="UI management and updates",
            )
        )

        # Shared modules
        scripts.append(
            ScriptSpec(
                name="Constants",
                script_type=ScriptType.MODULE,
                description="Game-wide constants and configuration",
            )
        )
        scripts.append(
            ScriptSpec(
                name="Types",
                script_type=ScriptType.MODULE,
                description="Shared type definitions",
            )
        )
        scripts.append(
            ScriptSpec(
                name="Utils",
                script_type=ScriptType.MODULE,
                description="Shared utility functions",
            )
        )

        return scripts
