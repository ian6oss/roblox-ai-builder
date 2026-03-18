"""Orchestrator - coordinates the entire generation pipeline."""

from __future__ import annotations

import asyncio

from roblox_ai_builder.core.models import GamePlan, GeneratedFile, GeneratedProject
from roblox_ai_builder.generators.asset_guide import AssetGuide
from roblox_ai_builder.generators.luau_generator import LuauGenerator
from roblox_ai_builder.generators.system_presets import SystemPresets
from roblox_ai_builder.generators.ui_builder import UIBuilder


class Orchestrator:
    """Coordinates the generation pipeline."""

    def __init__(
        self,
        luau_gen: LuauGenerator,
        ui_builder: UIBuilder,
        asset_guide: AssetGuide,
        presets: SystemPresets,
    ):
        self.luau_gen = luau_gen
        self.ui_builder = ui_builder
        self.asset_guide = asset_guide
        self.presets = presets

    async def run_pipeline(self, plan: GamePlan) -> GeneratedProject:
        """Execute the full generation pipeline."""
        # 1. Load preset files first (sync, fast)
        preset_files = self.presets.load(plan.preset_id, plan.systems)

        # 2. Run AI generation + UI + asset guide in parallel
        luau_task = self.luau_gen.generate(plan, preset_files)
        ui_task = self.ui_builder.generate(plan.ui_specs, plan.genre)
        asset_task = self.asset_guide.generate(plan.asset_hints, plan.genre)

        luau_files, ui_files, asset_guide_text = await asyncio.gather(
            luau_task, ui_task, asset_task
        )

        # 3. Merge all files (presets + AI-generated + UI)
        all_files = self._merge_files(preset_files, luau_files, ui_files)

        # 4. Build project
        return GeneratedProject(
            name=plan.game_name,
            genre=plan.genre,
            files=all_files,
            asset_guide=asset_guide_text,
            metadata={
                "systems": [s.value for s in plan.systems],
                "ui": [u.value for u in plan.ui_specs],
                "preset": plan.preset_id,
                "script_count": len(all_files),
            },
        )

    @staticmethod
    def _merge_files(*file_lists: list[GeneratedFile]) -> list[GeneratedFile]:
        """Merge file lists, resolving duplicates (AI > preset > template)."""
        seen: dict[str, GeneratedFile] = {}
        priority = {"ai": 3, "template": 2, "preset": 1, "fallback": 0}

        for file_list in file_lists:
            for f in file_list:
                existing = seen.get(f.path)
                if existing is None:
                    seen[f.path] = f
                else:
                    # Higher priority source wins
                    if priority.get(f.source, 0) > priority.get(existing.source, 0):
                        seen[f.path] = f

        return list(seen.values())
