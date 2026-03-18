"""Tests for UIBuilder."""

import asyncio

import pytest

from roblox_ai_builder.core.models import Genre, UIType
from roblox_ai_builder.generators.ui_builder import UIBuilder


@pytest.fixture
def builder():
    return UIBuilder(ai_client=None)


class TestUIBuilder:
    def test_generates_hud(self, builder: UIBuilder):
        files = asyncio.run(builder.generate([UIType.HUD], Genre.OBBY))
        assert len(files) == 1
        assert "HUD" in files[0].path
        assert "ScreenGui" in files[0].content

    def test_generates_multiple_ui(self, builder: UIBuilder):
        specs = [UIType.HUD, UIType.SHOP_GUI, UIType.INVENTORY_GUI]
        files = asyncio.run(builder.generate(specs, Genre.SURVIVAL))
        assert len(files) == 3
        paths = [f.path for f in files]
        assert any("HUD" in p for p in paths)
        assert any("ShopGui" in p for p in paths)
        assert any("InventoryGui" in p for p in paths)

    def test_wave_counter(self, builder: UIBuilder):
        files = asyncio.run(builder.generate([UIType.WAVE_COUNTER], Genre.SURVIVAL))
        assert len(files) == 1
        assert "WaveCounter" in files[0].path
        assert "CurrentWave" in files[0].content

    def test_all_templates_have_content(self, builder: UIBuilder):
        for ui_type in [UIType.HUD, UIType.SHOP_GUI, UIType.INVENTORY_GUI,
                        UIType.WAVE_COUNTER, UIType.MENU]:
            files = asyncio.run(builder.generate([ui_type], Genre.CUSTOM))
            assert len(files) == 1
            assert len(files[0].content) > 50

    def test_unknown_ui_gets_fallback(self, builder: UIBuilder):
        files = asyncio.run(builder.generate([UIType.DIALOG_GUI], Genre.CUSTOM))
        assert len(files) == 1
        assert files[0].source == "fallback"

    def test_all_files_go_to_starter_gui(self, builder: UIBuilder):
        files = asyncio.run(builder.generate(
            [UIType.HUD, UIType.SHOP_GUI], Genre.OBBY
        ))
        for f in files:
            assert f.path.startswith("src/StarterGui/")
