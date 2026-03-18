"""Tests for Orchestrator (integration test using no-AI mode)."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from roblox_ai_builder.core.game_planner import GamePlanner
from roblox_ai_builder.core.models import Genre, ParsedPrompt, SystemType, UIType
from roblox_ai_builder.core.orchestrator import Orchestrator
from roblox_ai_builder.core.prompt_engine import PromptEngine
from roblox_ai_builder.generators.asset_guide import AssetGuide
from roblox_ai_builder.generators.luau_generator import LuauGenerator
from roblox_ai_builder.generators.system_presets import SystemPresets
from roblox_ai_builder.generators.ui_builder import UIBuilder
from roblox_ai_builder.output.rojo_writer import RojoWriter
from roblox_ai_builder.utils.errors import RABError


class DummyAIClient:
    async def generate_luau_scripts(self, *args, **kwargs):
        raise RABError("No AI")


@pytest.fixture
def orchestrator():
    dummy = DummyAIClient()
    return Orchestrator(
        luau_gen=LuauGenerator(dummy),  # type: ignore
        ui_builder=UIBuilder(ai_client=None),
        asset_guide=AssetGuide(),
        presets=SystemPresets(),
    )


class TestOrchestratorIntegration:
    def test_obby_generation(self, orchestrator: Orchestrator):
        plan_input = ParsedPrompt(
            raw="obby game with leaderboard",
            genre=Genre.OBBY,
            systems=[SystemType.CHECKPOINT, SystemType.LEADERBOARD],
            ui_requests=[UIType.HUD],
            game_name="MyObby",
        )
        planner = GamePlanner()
        plan = planner.plan(plan_input)

        project = asyncio.run(orchestrator.run_pipeline(plan))

        assert project.name == "MyObby"
        assert project.genre == Genre.OBBY
        assert len(project.files) > 0
        assert project.asset_guide

        # Check that preset files are included
        file_paths = [f.path for f in project.files]
        assert any("CheckpointService" in p for p in file_paths)
        assert any("LeaderboardService" in p for p in file_paths)
        assert any("HUD" in p for p in file_paths)

    def test_survival_generation(self, orchestrator: Orchestrator):
        plan_input = ParsedPrompt(
            raw="zombie survival with inventory and shop",
            genre=Genre.SURVIVAL,
            systems=[
                SystemType.COMBAT, SystemType.INVENTORY,
                SystemType.SHOP, SystemType.ECONOMY,
                SystemType.WAVE_SPAWNER,
            ],
            ui_requests=[UIType.HUD, UIType.SHOP_GUI, UIType.INVENTORY_GUI, UIType.WAVE_COUNTER],
            game_name="ZombieSurvival",
        )
        planner = GamePlanner()
        plan = planner.plan(plan_input)

        project = asyncio.run(orchestrator.run_pipeline(plan))

        assert project.name == "ZombieSurvival"
        assert len(project.files) >= 8  # presets + UI + fallback scripts

        file_paths = [f.path for f in project.files]
        assert any("InventoryService" in p for p in file_paths)
        assert any("CombatService" in p for p in file_paths)
        assert any("ShopService" in p for p in file_paths)
        assert any("WaveManager" in p for p in file_paths)
        assert any("HUD" in p for p in file_paths)
        assert any("ShopGui" in p for p in file_paths)

    def test_full_e2e_to_disk(self, orchestrator: Orchestrator):
        """End-to-end: prompt -> parse -> plan -> generate -> write to disk."""
        engine = PromptEngine(ai_client=None)
        planner = GamePlanner()
        writer = RojoWriter()

        parsed = asyncio.run(engine.parse("tycoon game with economy"))
        plan = planner.plan(parsed)
        project = asyncio.run(orchestrator.run_pipeline(plan))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = writer.write(project, Path(tmpdir))
            assert output_path.exists()
            assert (output_path / "default.project.json").exists()
            assert (output_path / "ASSET_GUIDE.md").exists()
            assert (output_path / "README.md").exists()

            # Check Lua files exist
            lua_files = list(output_path.rglob("*.lua"))
            assert len(lua_files) > 0
