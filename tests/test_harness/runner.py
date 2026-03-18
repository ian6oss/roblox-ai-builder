"""Test runner — executes prompts through the pipeline and collects metrics."""

from __future__ import annotations

import asyncio
import tempfile
import traceback
from dataclasses import asdict
from pathlib import Path

from roblox_ai_builder.core.game_planner import GamePlanner
from roblox_ai_builder.core.models import (
    GeneratedFile,
    GeneratedProject,
    ParsedPrompt,
)
from roblox_ai_builder.core.orchestrator import Orchestrator
from roblox_ai_builder.core.prompt_engine import PromptEngine
from roblox_ai_builder.generators.asset_guide import AssetGuide
from roblox_ai_builder.generators.luau_generator import LuauGenerator
from roblox_ai_builder.generators.system_presets import SystemPresets
from roblox_ai_builder.generators.ui_builder import UIBuilder
from roblox_ai_builder.output.rojo_writer import RojoWriter
from roblox_ai_builder.utils.ai_client import AIClient

from tests.test_harness.metrics import StageMetric, TestResult
from tests.test_harness.test_prompts import TestPrompt


class TestRunner:
    """Runs a single test prompt through the full pipeline."""

    def __init__(
        self,
        ai_client: AIClient | None = None,
        output_dir: Path | None = None,
        write_to_disk: bool = True,
    ):
        self.ai_client = ai_client
        self.output_dir = output_dir or Path(tempfile.mkdtemp(prefix="rab_test_"))
        self.write_to_disk = write_to_disk

    async def run(self, test_prompt: TestPrompt) -> TestResult:
        """Execute a single test prompt through the full pipeline."""
        result = TestResult(
            prompt_id=test_prompt.id,
            level=test_prompt.level,
            prompt_text=test_prompt.prompt,
            description=test_prompt.description,
            expected_genre=test_prompt.expected_genre,
            systems_expected=test_prompt.expected_systems,
            min_files_expected=test_prompt.min_files,
        )
        result.start()

        try:
            # Stage 1: Prompt Parsing
            parsed = await self._stage_parse(test_prompt, result)
            if parsed is None:
                result.stop()
                return result

            # Stage 2: Game Planning
            plan = self._stage_plan(parsed, result)
            if plan is None:
                result.stop()
                return result

            # Stage 3: Code Generation
            project = await self._stage_generate(plan, result)
            if project is None:
                result.stop()
                return result

            # Stage 4: File Output (optional disk write)
            if self.write_to_disk:
                self._stage_write(project, result)

            # Stage 5: Validation
            self._stage_validate(test_prompt, parsed, plan, project, result)

        except Exception as e:
            result.add_error(f"Unexpected error: {e}\n{traceback.format_exc()}")

        result.stop()
        return result

    async def _stage_parse(
        self, test_prompt: TestPrompt, result: TestResult
    ) -> ParsedPrompt | None:
        """Stage 1: Parse the natural language prompt."""
        stage = StageMetric(stage="parse")
        stage.start()

        try:
            engine = PromptEngine(ai_client=self.ai_client)
            parsed = await engine.parse(test_prompt.prompt)

            stage.output_summary = {
                "genre": parsed.genre.value,
                "systems": [s.value for s in parsed.systems],
                "ui_requests": [u.value for u in parsed.ui_requests],
                "game_name": parsed.game_name,
                "language": parsed.language,
                "asset_hints": parsed.asset_hints,
            }

            result.raw_parsed_prompt = stage.output_summary
            result.actual_genre = parsed.genre.value

            stage.stop(success=True)
            result.add_stage(stage)
            return parsed

        except Exception as e:
            stage.stop(success=False, error=str(e))
            result.add_stage(stage)
            result.add_error(f"Parse failed: {e}")
            return None

    def _stage_plan(
        self, parsed: ParsedPrompt, result: TestResult
    ) -> "GamePlan | None":
        """Stage 2: Create game plan from parsed prompt."""
        from roblox_ai_builder.core.models import GamePlan

        stage = StageMetric(stage="plan")
        stage.start()

        try:
            planner = GamePlanner()
            plan = planner.plan(parsed)

            stage.output_summary = {
                "genre": plan.genre.value,
                "preset_id": plan.preset_id,
                "game_name": plan.game_name,
                "num_scripts": len(plan.scripts),
                "systems": [s.value for s in plan.systems],
                "scripts": [
                    {"name": s.name, "type": s.script_type.value, "desc": s.description}
                    for s in plan.scripts
                ],
            }

            result.raw_game_plan = stage.output_summary

            stage.stop(success=True)
            result.add_stage(stage)
            return plan

        except Exception as e:
            stage.stop(success=False, error=str(e))
            result.add_stage(stage)
            result.add_error(f"Planning failed: {e}")
            return None

    async def _stage_generate(
        self, plan, result: TestResult
    ) -> GeneratedProject | None:
        """Stage 3: Generate code via orchestrator."""
        stage = StageMetric(stage="generate")
        stage.start()

        try:
            # Build orchestrator with or without AI
            if self.ai_client:
                luau_gen = LuauGenerator(self.ai_client)
            else:
                # Use a dummy client that forces fallback
                luau_gen = LuauGenerator(_DummyAIClient())  # type: ignore

            orchestrator = Orchestrator(
                luau_gen=luau_gen,
                ui_builder=UIBuilder(ai_client=self.ai_client),
                asset_guide=AssetGuide(),
                presets=SystemPresets(),
            )

            project = await orchestrator.run_pipeline(plan)

            # Collect file metrics
            total_loc = 0
            file_manifest = []
            for f in project.files:
                loc = len(f.content.splitlines())
                total_loc += loc
                file_manifest.append({
                    "path": f.path,
                    "source": f.source,
                    "lines": loc,
                    "size_bytes": len(f.content.encode("utf-8")),
                })

            stage.output_summary = {
                "files_count": len(project.files),
                "total_loc": total_loc,
                "asset_guide_length": len(project.asset_guide),
            }

            result.files_generated = len(project.files)
            result.total_lines_of_code = total_loc
            result.file_manifest = file_manifest

            stage.stop(success=True)
            result.add_stage(stage)
            return project

        except Exception as e:
            stage.stop(success=False, error=str(e))
            result.add_stage(stage)
            result.add_error(f"Generation failed: {e}")
            return None

    def _stage_write(self, project: GeneratedProject, result: TestResult) -> None:
        """Stage 4: Write generated project to disk."""
        stage = StageMetric(stage="write")
        stage.start()

        try:
            writer = RojoWriter()
            output_path = writer.write(project, self.output_dir)

            stage.output_summary = {
                "output_path": str(output_path),
                "project_json_exists": (output_path / "default.project.json").exists(),
            }

            # Count actual files on disk
            lua_files = list(output_path.rglob("*.lua"))
            stage.output_summary["lua_files_on_disk"] = len(lua_files)

            stage.stop(success=True)
            result.add_stage(stage)

        except Exception as e:
            stage.stop(success=False, error=str(e))
            result.add_stage(stage)
            result.add_error(f"Write failed: {e}")

    def _stage_validate(
        self,
        test_prompt: TestPrompt,
        parsed: ParsedPrompt,
        plan,
        project: GeneratedProject,
        result: TestResult,
    ) -> None:
        """Stage 5: Validate outputs against expectations.

        Uses plan.systems (which includes genre defaults) for system validation,
        not just parsed.systems (keyword-only detection).
        """
        stage = StageMetric(stage="validate")
        stage.start()

        try:
            # Check genre match
            result.genre_match = parsed.genre.value == test_prompt.expected_genre

            # Check systems detection — use plan systems (includes genre defaults)
            detected = {s.value for s in plan.systems}
            expected = set(test_prompt.expected_systems)
            result.systems_detected = sorted(detected)
            result.systems_missing = sorted(expected - detected)

            if expected:
                result.system_match_ratio = len(expected & detected) / len(expected)
            else:
                result.system_match_ratio = 1.0

            # Check minimum files
            result.files_met_minimum = result.files_generated >= test_prompt.min_files

            # Add validation errors for failures
            if not result.genre_match:
                result.add_error(
                    f"Genre mismatch: expected={test_prompt.expected_genre}, "
                    f"actual={parsed.genre.value}"
                )
            if result.systems_missing:
                result.add_error(
                    f"Missing systems: {', '.join(result.systems_missing)}"
                )
            if not result.files_met_minimum:
                result.add_error(
                    f"Insufficient files: {result.files_generated} < {test_prompt.min_files}"
                )

            stage.output_summary = {
                "genre_match": result.genre_match,
                "system_match_ratio": result.system_match_ratio,
                "files_met_minimum": result.files_met_minimum,
                "missing_systems": result.systems_missing,
            }

            stage.stop(success=True)
            result.add_stage(stage)

        except Exception as e:
            stage.stop(success=False, error=str(e))
            result.add_stage(stage)


class _DummyAIClient:
    """Dummy AI client that raises to trigger fallback code generation."""

    async def generate_luau_scripts(self, *args, **kwargs):
        from roblox_ai_builder.utils.errors import AIGenerationError
        raise AIGenerationError("No AI client configured — using fallback generation")

    async def generate(self, *args, **kwargs):
        from roblox_ai_builder.utils.errors import AIGenerationError
        raise AIGenerationError("No AI client configured — using fallback generation")

    async def generate_json(self, *args, **kwargs):
        from roblox_ai_builder.utils.errors import AIGenerationError
        raise AIGenerationError("No AI client configured — using fallback generation")
