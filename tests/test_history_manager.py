"""Tests for HistoryManager."""

import tempfile
from pathlib import Path

import pytest

from roblox_ai_builder.output.history_manager import HistoryManager


@pytest.fixture
def hm():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield HistoryManager(history_path=Path(tmpdir) / "history.json")


class TestHistoryManager:
    def test_save_and_list(self, hm: HistoryManager):
        record_id = hm.save(
            prompt="obby game",
            genre="obby",
            game_name="MyObby",
            output_dir="/tmp/output/MyObby",
            file_count=5,
            systems=["checkpoint", "leaderboard"],
        )
        assert record_id == "gen_0001"

        records = hm.list_records()
        assert len(records) == 1
        assert records[0]["game_name"] == "MyObby"

    def test_get_record(self, hm: HistoryManager):
        hm.save("test", "obby", "Test", "/tmp", 3, ["checkpoint"])
        record = hm.get_record("gen_0001")
        assert record is not None
        assert record["genre"] == "obby"

    def test_get_nonexistent_record(self, hm: HistoryManager):
        assert hm.get_record("gen_9999") is None

    def test_empty_history(self, hm: HistoryManager):
        assert hm.list_records() == []

    def test_multiple_records(self, hm: HistoryManager):
        hm.save("test1", "obby", "Game1", "/tmp/1", 3, [])
        hm.save("test2", "tycoon", "Game2", "/tmp/2", 5, [])
        hm.save("test3", "fps", "Game3", "/tmp/3", 8, [])

        records = hm.list_records()
        assert len(records) == 3
        assert records[2]["id"] == "gen_0003"
