"""Tests for Config."""

import os
import tempfile
from pathlib import Path

import pytest

from roblox_ai_builder.utils.config import Config


class TestConfig:
    def test_default_config(self):
        config = Config()
        assert config.api_key == ""
        assert "claude" in config.model
        assert config.max_tokens == 8192

    def test_load_nonexistent_file(self):
        config = Config.load(Path("/nonexistent/config.toml"))
        assert config.api_key == ""

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
        config = Config.load(Path("/nonexistent/config.toml"))
        assert config.api_key == "test-key-123"

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            config = Config()
            config.api_key = "sk-test"
            config.model = "claude-sonnet-4-6-20250514"
            config.save(path)

            loaded = Config.load(path)
            assert loaded.api_key == "sk-test"
            assert loaded.model == "claude-sonnet-4-6-20250514"

    def test_validate_missing_key(self):
        config = Config()
        errors = config.validate()
        assert len(errors) == 1
        assert "API key" in errors[0]

    def test_validate_with_key(self):
        config = Config(api_key="sk-test")
        errors = config.validate()
        assert len(errors) == 0

    def test_output_dir_env(self, monkeypatch):
        monkeypatch.setenv("ROBLOX_AI_BUILDER_OUTPUT", "/tmp/custom")
        config = Config.load(Path("/nonexistent/config.toml"))
        assert str(config.output_dir) == "/tmp/custom"
