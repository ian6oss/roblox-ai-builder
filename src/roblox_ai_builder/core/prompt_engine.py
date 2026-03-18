"""Prompt parsing engine - converts natural language to structured game requirements."""

from __future__ import annotations

import re

from roblox_ai_builder.core.models import (
    GENRE_KEYWORDS,
    SYSTEM_DEPENDENCIES,
    SYSTEM_KEYWORDS,
    SYSTEM_UI_MAPPING,
    UI_KEYWORDS,
    Genre,
    ParsedPrompt,
    SystemType,
    UIType,
)
from roblox_ai_builder.utils.ai_client import AIClient
from roblox_ai_builder.utils.errors import PromptParseError


PARSE_SYSTEM_PROMPT = """You are a Roblox game design analyzer. Given a natural language prompt
(in any language), extract structured game requirements.

Output ONLY valid JSON with this schema:
{
  "genre": "obby|tycoon|simulator|rpg|fps|survival|horror|racing|custom",
  "game_name": "suggested english name in PascalCase (e.g. ZombieSurvival)",
  "systems": ["inventory", "combat", "shop", "leaderboard", "wave_spawner", "economy", "crafting", "quest", "dialog", "gamepass", "checkpoint", "tycoon_core", "pet"],
  "ui_requests": ["hud", "shop_gui", "inventory_gui", "menu", "settings", "leaderboard_gui", "dialog_gui", "wave_counter"],
  "asset_hints": ["zombie", "sword", "terrain", ...],
  "custom_params": {}
}

Rules:
- Always include "hud" in ui_requests
- Infer implicit systems (e.g., "shop" implies "economy" and "inventory")
- If genre is ambiguous, pick the closest match
- game_name should be short and descriptive PascalCase
- asset_hints: list physical objects/characters the game needs"""


class PromptEngine:
    """Parses natural language prompts into structured game requirements."""

    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client

    async def parse(self, raw_prompt: str) -> ParsedPrompt:
        """Parse a natural language prompt into structured requirements."""
        if not raw_prompt.strip():
            raise PromptParseError("Prompt cannot be empty")

        language = self._detect_language(raw_prompt)

        if self.ai_client:
            return await self._ai_parse(raw_prompt, language)
        return self._local_parse(raw_prompt, language)

    async def _ai_parse(self, raw: str, language: str) -> ParsedPrompt:
        """Parse using Claude API for high-quality extraction."""
        assert self.ai_client is not None

        try:
            result = await self.ai_client.generate_json(
                prompt=f"Analyze this game prompt:\n\n{raw}",
                system=PARSE_SYSTEM_PROMPT,
            )
        except Exception:
            # Fallback to local parsing
            return self._local_parse(raw, language)

        genre = self._safe_genre(result.get("genre", "custom"))
        systems = self._safe_systems(result.get("systems", []))
        ui_requests = self._safe_ui(result.get("ui_requests", ["hud"]))
        systems = self._resolve_dependencies(systems)

        # Ensure implied UIs
        for system in systems:
            if system in SYSTEM_UI_MAPPING:
                for ui in SYSTEM_UI_MAPPING[system]:
                    if ui not in ui_requests:
                        ui_requests.append(ui)

        if UIType.HUD not in ui_requests:
            ui_requests.insert(0, UIType.HUD)

        return ParsedPrompt(
            raw=raw,
            language=language,
            genre=genre,
            systems=systems,
            ui_requests=ui_requests,
            asset_hints=result.get("asset_hints", []),
            custom_params=result.get("custom_params", {}),
            game_name=result.get("game_name", "MyGame"),
        )

    def _local_parse(self, raw: str, language: str) -> ParsedPrompt:
        """Parse using keyword matching (no API needed)."""
        lower = raw.lower()

        genre = self._detect_genre(lower)
        systems = self._detect_systems(lower)
        ui_requests = self._detect_ui(lower)
        systems = self._resolve_dependencies(systems)

        # Auto-add UIs for detected systems
        for system in systems:
            if system in SYSTEM_UI_MAPPING:
                for ui in SYSTEM_UI_MAPPING[system]:
                    if ui not in ui_requests:
                        ui_requests.append(ui)

        if UIType.HUD not in ui_requests:
            ui_requests.insert(0, UIType.HUD)

        game_name = self._generate_name(genre, systems)

        return ParsedPrompt(
            raw=raw,
            language=language,
            genre=genre,
            systems=systems,
            ui_requests=ui_requests,
            asset_hints=self._extract_asset_hints(lower, genre),
            game_name=game_name,
        )

    @staticmethod
    def _detect_language(text: str) -> str:
        """Detect prompt language."""
        if re.search(r"[\uac00-\ud7af\u3130-\u318f]", text):
            return "ko"
        if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", text):
            return "ja"
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        return "en"

    @staticmethod
    def _detect_genre(text: str) -> Genre:
        """Detect genre from keywords, preferring the earliest match in the text."""
        best_pos = len(text)
        best_genre = Genre.CUSTOM
        for keyword, genre in GENRE_KEYWORDS.items():
            pos = text.find(keyword)
            if pos != -1 and pos < best_pos:
                best_pos = pos
                best_genre = genre
        return best_genre

    @staticmethod
    def _detect_systems(text: str) -> list[SystemType]:
        """Detect game systems from keywords."""
        found: list[SystemType] = []
        for keyword, system in SYSTEM_KEYWORDS.items():
            if keyword in text and system not in found:
                found.append(system)
        return found

    @staticmethod
    def _detect_ui(text: str) -> list[UIType]:
        """Detect UI components from keywords."""
        found: list[UIType] = []
        for keyword, ui in UI_KEYWORDS.items():
            if keyword in text and ui not in found:
                found.append(ui)
        return found

    @staticmethod
    def _resolve_dependencies(systems: list[SystemType]) -> list[SystemType]:
        """Resolve system dependencies (add missing deps)."""
        resolved = list(systems)
        changed = True
        while changed:
            changed = False
            for system in list(resolved):
                deps = SYSTEM_DEPENDENCIES.get(system, [])
                for dep in deps:
                    if dep not in resolved:
                        resolved.append(dep)
                        changed = True
        return resolved

    @staticmethod
    def _safe_genre(value: str) -> Genre:
        """Safely convert string to Genre enum."""
        try:
            return Genre(value)
        except ValueError:
            return Genre.CUSTOM

    @staticmethod
    def _safe_systems(values: list[str]) -> list[SystemType]:
        """Safely convert strings to SystemType enums."""
        result = []
        for v in values:
            try:
                result.append(SystemType(v))
            except ValueError:
                pass
        return result

    @staticmethod
    def _safe_ui(values: list[str]) -> list[UIType]:
        """Safely convert strings to UIType enums."""
        result = []
        for v in values:
            try:
                result.append(UIType(v))
            except ValueError:
                pass
        return result

    @staticmethod
    def _generate_name(genre: Genre, systems: list[SystemType]) -> str:
        """Generate a game name from genre and systems."""
        genre_names = {
            Genre.OBBY: "ObstacleCourse",
            Genre.TYCOON: "Tycoon",
            Genre.SIMULATOR: "Simulator",
            Genre.RPG: "RPGAdventure",
            Genre.FPS: "ShooterArena",
            Genre.SURVIVAL: "Survival",
            Genre.HORROR: "HorrorEscape",
            Genre.RACING: "RacingGame",
            Genre.CUSTOM: "MyGame",
        }
        return genre_names.get(genre, "MyGame")

    @staticmethod
    def _extract_asset_hints(text: str, genre: Genre) -> list[str]:
        """Extract asset hints from text and genre defaults."""
        hints: list[str] = []
        genre_assets: dict[Genre, list[str]] = {
            Genre.OBBY: ["platforms", "obstacles", "checkpoints", "decorations"],
            Genre.TYCOON: ["buttons", "conveyors", "machines", "droppers"],
            Genre.SIMULATOR: ["tools", "pets", "zones", "upgrades"],
            Genre.RPG: ["weapons", "armor", "npcs", "dungeons"],
            Genre.FPS: ["weapons", "ammo", "cover", "spawn_points"],
            Genre.SURVIVAL: ["weapons", "zombies", "barricades", "supplies"],
            Genre.HORROR: ["flashlight", "doors", "monsters", "keys"],
            Genre.RACING: ["vehicles", "track", "boosts", "checkpoints"],
        }
        hints.extend(genre_assets.get(genre, ["terrain", "decorations"]))
        return hints
