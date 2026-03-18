"""Tests for GamePlanner."""

import asyncio

import pytest

from roblox_ai_builder.core.game_planner import GamePlanner
from roblox_ai_builder.core.models import Genre, ParsedPrompt, ScriptType, SystemType, UIType
from roblox_ai_builder.core.prompt_engine import PromptEngine


@pytest.fixture
def planner():
    return GamePlanner()


@pytest.fixture
def engine():
    return PromptEngine(ai_client=None)


class TestGamePlanCreation:
    def test_obby_plan(self, planner: GamePlanner):
        parsed = ParsedPrompt(
            raw="obby game",
            genre=Genre.OBBY,
            systems=[],
            ui_requests=[UIType.HUD],
            game_name="ObstacleCourse",
        )
        plan = planner.plan(parsed)
        assert plan.genre == Genre.OBBY
        assert plan.preset_id == "obby"
        assert SystemType.CHECKPOINT in plan.systems
        assert SystemType.LEADERBOARD in plan.systems

    def test_survival_plan(self, planner: GamePlanner):
        parsed = ParsedPrompt(
            raw="survival game",
            genre=Genre.SURVIVAL,
            systems=[SystemType.SHOP],
            ui_requests=[UIType.HUD, UIType.SHOP_GUI],
            game_name="Survival",
        )
        plan = planner.plan(parsed)
        assert SystemType.COMBAT in plan.systems
        assert SystemType.INVENTORY in plan.systems
        assert SystemType.SHOP in plan.systems

    def test_always_has_game_manager(self, planner: GamePlanner):
        parsed = ParsedPrompt(raw="test", genre=Genre.CUSTOM, game_name="Test")
        plan = planner.plan(parsed)
        script_names = [s.name for s in plan.scripts]
        assert "GameManager" in script_names

    def test_has_client_scripts(self, planner: GamePlanner):
        parsed = ParsedPrompt(raw="test", genre=Genre.OBBY, game_name="Test")
        plan = planner.plan(parsed)
        client_scripts = [s for s in plan.scripts if s.script_type == ScriptType.CLIENT]
        assert len(client_scripts) >= 2  # InputHandler + UIController

    def test_has_shared_modules(self, planner: GamePlanner):
        parsed = ParsedPrompt(raw="test", genre=Genre.OBBY, game_name="Test")
        plan = planner.plan(parsed)
        modules = [s for s in plan.scripts if s.script_type == ScriptType.MODULE]
        assert len(modules) >= 2  # Constants + Types + Utils


class TestEndToEnd:
    def test_full_pipeline_prompt_to_plan(self, engine: PromptEngine, planner: GamePlanner):
        parsed = asyncio.run(engine.parse("좀비 서바이벌 게임, 인벤토리 시스템, 상점 UI 포함"))
        plan = planner.plan(parsed)

        assert plan.genre == Genre.SURVIVAL
        assert SystemType.INVENTORY in plan.systems
        assert SystemType.SHOP in plan.systems
        assert SystemType.COMBAT in plan.systems
        assert len(plan.scripts) > 5
