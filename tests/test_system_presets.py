"""Tests for SystemPresets."""

import pytest

from roblox_ai_builder.core.models import SystemType
from roblox_ai_builder.generators.system_presets import SystemPresets


@pytest.fixture
def presets():
    return SystemPresets()


class TestSystemPresets:
    def test_list_presets(self, presets: SystemPresets):
        available = presets.list_presets()
        assert "obby" in available
        assert "tycoon" in available

    def test_load_obby_preset(self, presets: SystemPresets):
        files = presets.load("obby", [SystemType.CHECKPOINT, SystemType.LEADERBOARD])
        assert len(files) >= 2
        paths = [f.path for f in files]
        assert any("CheckpointService" in p for p in paths)
        assert any("LeaderboardService" in p for p in paths)

    def test_load_tycoon_preset(self, presets: SystemPresets):
        files = presets.load("tycoon", [SystemType.TYCOON_CORE, SystemType.ECONOMY])
        assert len(files) >= 2
        paths = [f.path for f in files]
        assert any("TycoonService" in p for p in paths)
        assert any("EconomyService" in p for p in paths)

    def test_load_common_systems(self, presets: SystemPresets):
        files = presets.load("obby", [
            SystemType.CHECKPOINT, SystemType.INVENTORY,
            SystemType.COMBAT, SystemType.SHOP,
        ])
        paths = [f.path for f in files]
        assert any("InventoryService" in p for p in paths)
        assert any("CombatService" in p for p in paths)
        assert any("ShopService" in p for p in paths)

    def test_all_preset_files_are_server_scripts(self, presets: SystemPresets):
        files = presets.load("obby", [SystemType.CHECKPOINT])
        for f in files:
            assert "ServerScriptService" in f.path

    def test_preset_source_tag(self, presets: SystemPresets):
        files = presets.load("obby", [SystemType.CHECKPOINT])
        for f in files:
            assert f.source == "preset"

    def test_empty_systems_returns_genre_presets(self, presets: SystemPresets):
        files = presets.load("obby", [])
        # Should still return the obby genre presets
        assert len(files) >= 2

    def test_wave_manager_preset(self, presets: SystemPresets):
        files = presets.load("obby", [SystemType.WAVE_SPAWNER])
        paths = [f.path for f in files]
        assert any("WaveManager" in p for p in paths)
