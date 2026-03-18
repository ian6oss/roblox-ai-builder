"""Tests for PromptEngine."""

import pytest

from roblox_ai_builder.core.models import Genre, SystemType, UIType
from roblox_ai_builder.core.prompt_engine import PromptEngine


@pytest.fixture
def engine():
    return PromptEngine(ai_client=None)


class TestLanguageDetection:
    def test_korean(self, engine: PromptEngine):
        parsed = pytest.importorskip("asyncio").run(engine.parse("좀비 서바이벌 게임"))
        assert parsed.language == "ko"

    def test_english(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("zombie survival game"))
        assert parsed.language == "en"


class TestGenreDetection:
    @pytest.mark.parametrize(
        "prompt,expected_genre",
        [
            ("obby game with 20 levels", Genre.OBBY),
            ("장애물 코스 게임", Genre.OBBY),
            ("tycoon business game", Genre.TYCOON),
            ("타이쿤 게임 만들어줘", Genre.TYCOON),
            ("zombie survival game", Genre.SURVIVAL),
            ("좀비 서바이벌", Genre.SURVIVAL),
            ("fps shooter arena", Genre.FPS),
            ("rpg adventure quest", Genre.RPG),
            ("simulator game with pets", Genre.SIMULATOR),
            ("racing game", Genre.RACING),
            ("horror escape room", Genre.HORROR),
            ("some random game", Genre.CUSTOM),
        ],
    )
    def test_genre_detection(self, engine: PromptEngine, prompt: str, expected_genre: Genre):
        import asyncio
        parsed = asyncio.run(engine.parse(prompt))
        assert parsed.genre == expected_genre


class TestSystemDetection:
    def test_detects_inventory(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("game with inventory system"))
        assert SystemType.INVENTORY in parsed.systems

    def test_detects_korean_systems(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("인벤토리, 상점 포함된 게임"))
        assert SystemType.INVENTORY in parsed.systems
        assert SystemType.SHOP in parsed.systems

    def test_dependency_resolution(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("game with shop"))
        # Shop should pull in inventory and economy
        assert SystemType.SHOP in parsed.systems
        assert SystemType.INVENTORY in parsed.systems
        assert SystemType.ECONOMY in parsed.systems

    def test_wave_implies_combat(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("wave based game"))
        assert SystemType.WAVE_SPAWNER in parsed.systems
        assert SystemType.COMBAT in parsed.systems


class TestUIDetection:
    def test_always_includes_hud(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("simple obby game"))
        assert UIType.HUD in parsed.ui_requests

    def test_system_implies_ui(self, engine: PromptEngine):
        import asyncio
        parsed = asyncio.run(engine.parse("game with inventory and shop"))
        assert UIType.INVENTORY_GUI in parsed.ui_requests
        assert UIType.SHOP_GUI in parsed.ui_requests


class TestEdgeCases:
    def test_empty_prompt_raises(self, engine: PromptEngine):
        import asyncio
        from roblox_ai_builder.utils.errors import PromptParseError
        with pytest.raises(PromptParseError):
            asyncio.run(engine.parse(""))

    def test_whitespace_prompt_raises(self, engine: PromptEngine):
        import asyncio
        from roblox_ai_builder.utils.errors import PromptParseError
        with pytest.raises(PromptParseError):
            asyncio.run(engine.parse("   "))
