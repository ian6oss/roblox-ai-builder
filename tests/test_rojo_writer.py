"""Tests for RojoWriter."""

import json
import tempfile
from pathlib import Path

import pytest

from roblox_ai_builder.core.models import GeneratedFile, GeneratedProject, Genre
from roblox_ai_builder.output.rojo_writer import RojoWriter


@pytest.fixture
def writer():
    return RojoWriter()


@pytest.fixture
def sample_project():
    return GeneratedProject(
        name="TestGame",
        genre=Genre.OBBY,
        files=[
            GeneratedFile(
                path="src/ServerScriptService/GameManager.server.lua",
                content='print("Hello")',
                source="ai",
            ),
            GeneratedFile(
                path="src/StarterPlayerScripts/InputHandler.client.lua",
                content='print("Client")',
                source="ai",
            ),
            GeneratedFile(
                path="src/ReplicatedStorage/Constants.lua",
                content="return {}",
                source="preset",
            ),
            GeneratedFile(
                path="src/StarterGui/HUD.client.lua",
                content='print("HUD")',
                source="template",
            ),
        ],
        asset_guide="# Assets\nPlace stuff here",
        metadata={
            "systems": ["checkpoint"],
            "ui": ["hud"],
            "preset": "obby",
            "script_count": 4,
        },
    )


class TestRojoWriter:
    def test_creates_project_dir(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))
            assert result.exists()
            assert result.name == "TestGame"

    def test_creates_rojo_dirs(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))
            for d in RojoWriter.ROJO_DIRS:
                assert (result / d).is_dir()

    def test_writes_project_json(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))
            config_path = result / "default.project.json"
            assert config_path.exists()

            config = json.loads(config_path.read_text())
            assert config["name"] == "TestGame"
            assert "ServerScriptService" in config["tree"]

    def test_writes_all_files(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))

            for f in sample_project.files:
                assert (result / f.path).exists()
                assert (result / f.path).read_text() == f.content

    def test_writes_asset_guide(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))
            guide = result / "ASSET_GUIDE.md"
            assert guide.exists()
            assert "Assets" in guide.read_text()

    def test_writes_readme(self, writer: RojoWriter, sample_project: GeneratedProject):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = writer.write(sample_project, Path(tmpdir))
            readme = result / "README.md"
            assert readme.exists()
            assert "TestGame" in readme.read_text()

    def test_sanitizes_name(self, writer: RojoWriter):
        assert writer._sanitize_name("My Game!@#") == "My-Game"
        assert writer._sanitize_name("  ") == "MyGame"
        assert writer._sanitize_name("Normal") == "Normal"
