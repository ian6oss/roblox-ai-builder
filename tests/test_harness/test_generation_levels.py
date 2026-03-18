"""Pytest-compatible tests for prompt-to-code generation across complexity levels.

Run with:
    pytest tests/test_harness/test_generation_levels.py -v
    pytest tests/test_harness/test_generation_levels.py -v -k "simple"
    pytest tests/test_harness/test_generation_levels.py -v -k "medium"
    pytest tests/test_harness/test_generation_levels.py -v -k "full"
"""

from __future__ import annotations

import pytest

from tests.test_harness.runner import TestRunner
from tests.test_harness.test_prompts import (
    FULL_PROMPTS,
    MEDIUM_PROMPTS,
    SIMPLE_PROMPTS,
    TestPrompt,
)


@pytest.fixture
def runner():
    """Test runner without AI (uses fallback generation)."""
    return TestRunner(ai_client=None, write_to_disk=False)


# ─── Simple level tests ───────────────────────────────────────────────


@pytest.mark.parametrize(
    "test_prompt",
    SIMPLE_PROMPTS,
    ids=[p.id for p in SIMPLE_PROMPTS],
)
@pytest.mark.asyncio
async def test_simple_prompts(runner: TestRunner, test_prompt: TestPrompt):
    """Test simple single-domain prompt parsing and generation."""
    result = await runner.run(test_prompt)

    assert result.genre_match, (
        f"Genre mismatch: expected={result.expected_genre}, actual={result.actual_genre}"
    )
    assert result.files_met_minimum, (
        f"Insufficient files: {result.files_generated} < {result.min_files_expected}"
    )
    # Simple prompts should complete quickly (under 5 seconds without AI)
    assert result.total_duration_ms < 5000, (
        f"Too slow: {result.total_duration_ms:.0f}ms"
    )


# ─── Medium level tests ───────────────────────────────────────────────


@pytest.mark.parametrize(
    "test_prompt",
    MEDIUM_PROMPTS,
    ids=[p.id for p in MEDIUM_PROMPTS],
)
@pytest.mark.asyncio
async def test_medium_prompts(runner: TestRunner, test_prompt: TestPrompt):
    """Test medium multi-domain prompt parsing and generation."""
    result = await runner.run(test_prompt)

    assert result.genre_match, (
        f"Genre mismatch: expected={result.expected_genre}, actual={result.actual_genre}"
    )
    assert result.files_met_minimum, (
        f"Insufficient files: {result.files_generated} < {result.min_files_expected}"
    )
    # Medium should detect at least 50% of expected systems
    assert result.system_match_ratio >= 0.5, (
        f"Low system detection: {result.system_match_ratio:.0%}, "
        f"missing: {result.systems_missing}"
    )


# ─── Full level tests ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "test_prompt",
    FULL_PROMPTS,
    ids=[p.id for p in FULL_PROMPTS],
)
@pytest.mark.asyncio
async def test_full_prompts(runner: TestRunner, test_prompt: TestPrompt):
    """Test full 10+ domain prompt parsing and generation."""
    result = await runner.run(test_prompt)

    assert result.genre_match, (
        f"Genre mismatch: expected={result.expected_genre}, actual={result.actual_genre}"
    )
    assert result.files_generated >= 10, (
        f"Full games should have at least 10 files, got {result.files_generated}"
    )
    # Full prompts should detect most expected systems
    assert result.system_match_ratio >= 0.4, (
        f"Low system detection: {result.system_match_ratio:.0%}, "
        f"missing: {result.systems_missing}"
    )


# ─── Cross-level aggregate tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_complexity_scaling(runner: TestRunner):
    """Verify that higher complexity prompts produce more files and LOC."""
    simple_result = await runner.run(SIMPLE_PROMPTS[0])
    medium_result = await runner.run(MEDIUM_PROMPTS[0])
    full_result = await runner.run(FULL_PROMPTS[0])

    # Files should increase with complexity
    assert full_result.files_generated >= medium_result.files_generated, (
        f"Full ({full_result.files_generated}) should have >= files than "
        f"medium ({medium_result.files_generated})"
    )
    assert medium_result.files_generated >= simple_result.files_generated, (
        f"Medium ({medium_result.files_generated}) should have >= files than "
        f"simple ({simple_result.files_generated})"
    )

    # LOC should increase with complexity
    assert full_result.total_lines_of_code >= medium_result.total_lines_of_code, (
        f"Full LOC ({full_result.total_lines_of_code}) should be >= "
        f"medium LOC ({medium_result.total_lines_of_code})"
    )
