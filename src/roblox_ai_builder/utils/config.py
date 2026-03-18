"""Configuration management for Roblox AI Builder."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "roblox-ai-builder" / "config.toml"
DEFAULT_OUTPUT_DIR = Path.cwd() / "output"


@dataclass
class Config:
    """Application configuration."""

    api_key: str = ""
    model: str = "claude-sonnet-4-6-20250514"
    max_tokens: int = 8192
    output_dir: Path = field(default_factory=lambda: DEFAULT_OUTPUT_DIR)
    presets_dir: Path | None = None
    language: str = "auto"

    @classmethod
    def load(cls, config_path: Path | None = None) -> Config:
        """Load configuration from TOML file and environment variables."""
        config = cls()

        path = config_path or Path(
            os.environ.get("ROBLOX_AI_BUILDER_CONFIG", str(DEFAULT_CONFIG_PATH))
        )

        if path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)

            ai = data.get("ai", {})
            config.api_key = ai.get("api_key", config.api_key)
            config.model = ai.get("model", config.model)
            config.max_tokens = ai.get("max_tokens", config.max_tokens)

            output = data.get("output", {})
            if "dir" in output:
                config.output_dir = Path(output["dir"])

            if "presets_dir" in data.get("general", {}):
                config.presets_dir = Path(data["general"]["presets_dir"])

            config.language = data.get("general", {}).get("language", config.language)

        # Environment variables override file config
        env_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if env_key:
            config.api_key = env_key

        env_output = os.environ.get("ROBLOX_AI_BUILDER_OUTPUT", "")
        if env_output:
            config.output_dir = Path(env_output)

        return config

    def save(self, config_path: Path | None = None) -> None:
        """Save configuration to TOML file."""
        path = config_path or DEFAULT_CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""[ai]
api_key = "{self.api_key}"
model = "{self.model}"
max_tokens = {self.max_tokens}

[output]
dir = "{self.output_dir}"

[general]
language = "{self.language}"
"""
        path.write_text(content)

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not self.api_key:
            errors.append(
                "API key not set. Run `rab config set api-key <key>` "
                "or set ANTHROPIC_API_KEY environment variable."
            )
        return errors
