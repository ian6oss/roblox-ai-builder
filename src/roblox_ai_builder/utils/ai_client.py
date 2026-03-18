"""Claude API client for Roblox AI Builder."""

from __future__ import annotations

import json
import re

from anthropic import AsyncAnthropic

from roblox_ai_builder.utils.errors import AIGenerationError


class AIClient:
    """Async Claude API client. Supports API key or OAuth token auth."""

    DEFAULT_MODEL = "claude-sonnet-4-6-20250514"
    MAX_TOKENS = 8192

    def __init__(
        self,
        api_key: str | None = None,
        auth_token: str | None = None,
        model: str | None = None,
    ):
        kwargs: dict = {}
        if api_key:
            kwargs["api_key"] = api_key
        if auth_token:
            kwargs["auth_token"] = auth_token
        # If neither is provided, AsyncAnthropic will check env vars:
        # ANTHROPIC_API_KEY and ANTHROPIC_AUTH_TOKEN
        self.client = AsyncAnthropic(**kwargs)
        self.model = model or self.DEFAULT_MODEL

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        """Generate text via Claude API."""
        try:
            messages = [{"role": "user", "content": prompt}]
            kwargs: dict = {
                "model": self.model,
                "max_tokens": max_tokens or self.MAX_TOKENS,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system

            response = await self.client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            raise AIGenerationError(f"Claude API call failed: {e}") from e

    async def generate_json(
        self,
        prompt: str,
        system: str = "",
    ) -> dict:
        """Generate structured JSON response via Claude API."""
        full_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: Respond with ONLY valid JSON. No markdown, no explanation, "
            "no code fences. Just the JSON object."
        )
        text = await self.generate(full_prompt, system=system)

        # Extract JSON from response (handle markdown fences if present)
        json_match = re.search(r"\{[\s\S]*\}", text)
        if not json_match:
            raise AIGenerationError(f"No JSON found in response: {text[:200]}")

        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            raise AIGenerationError(f"Invalid JSON in response: {e}") from e

    async def generate_luau_scripts(
        self,
        prompt: str,
        system: str = "",
    ) -> dict[str, str]:
        """Generate multiple Luau scripts from a single prompt.

        Returns dict mapping filename to code content.
        """
        text = await self.generate(prompt, system=system, max_tokens=16384)
        return self._parse_code_blocks(text)

    @staticmethod
    def _parse_code_blocks(text: str) -> dict[str, str]:
        """Parse ```lua:filename blocks from AI response."""
        scripts: dict[str, str] = {}
        pattern = r"```lua(?::([^\n]+))?\n([\s\S]*?)```"
        matches = re.finditer(pattern, text)

        for match in matches:
            filename = match.group(1) or f"Script_{len(scripts)}.lua"
            filename = filename.strip()
            code = match.group(2).strip()
            if code:
                scripts[filename] = code

        return scripts
