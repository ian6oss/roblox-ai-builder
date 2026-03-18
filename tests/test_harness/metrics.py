"""Metrics collection and reporting for test harness runs."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tests.test_harness.test_prompts import TestPrompt


@dataclass
class StageMetric:
    """Metrics for a single pipeline stage."""

    stage: str
    started_at: float = 0.0
    ended_at: float = 0.0
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None
    output_summary: dict = field(default_factory=dict)

    def start(self) -> None:
        self.started_at = time.time()

    def stop(self, success: bool = True, error: str | None = None) -> None:
        self.ended_at = time.time()
        self.duration_ms = (self.ended_at - self.started_at) * 1000
        self.success = success
        self.error = error


@dataclass
class TestResult:
    """Complete result for a single test prompt run."""

    prompt_id: str
    level: str
    prompt_text: str
    description: str
    started_at: float = 0.0
    ended_at: float = 0.0
    total_duration_ms: float = 0.0
    overall_success: bool = False
    stages: list[StageMetric] = field(default_factory=list)
    # Validation checks
    genre_match: bool = False
    expected_genre: str = ""
    actual_genre: str = ""
    systems_detected: list[str] = field(default_factory=list)
    systems_expected: list[str] = field(default_factory=list)
    systems_missing: list[str] = field(default_factory=list)
    system_match_ratio: float = 0.0
    files_generated: int = 0
    min_files_expected: int = 0
    files_met_minimum: bool = False
    total_lines_of_code: int = 0
    # Raw outputs
    raw_parsed_prompt: dict = field(default_factory=dict)
    raw_game_plan: dict = field(default_factory=dict)
    file_manifest: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def start(self) -> None:
        self.started_at = time.time()

    def stop(self) -> None:
        self.ended_at = time.time()
        self.total_duration_ms = (self.ended_at - self.started_at) * 1000
        self.overall_success = all(s.success for s in self.stages) and not self.errors

    def add_stage(self, stage: StageMetric) -> None:
        self.stages.append(stage)

    def add_error(self, error: str) -> None:
        self.errors.append(error)


@dataclass
class TestRunSummary:
    """Summary of an entire test harness run."""

    run_id: str
    started_at: float = 0.0
    ended_at: float = 0.0
    total_duration_ms: float = 0.0
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    results: list[TestResult] = field(default_factory=list)
    # Aggregated metrics
    avg_duration_by_level: dict[str, float] = field(default_factory=dict)
    avg_systems_match_ratio: float = 0.0
    avg_files_generated: float = 0.0
    avg_lines_of_code: float = 0.0
    genre_accuracy: float = 0.0

    def start(self) -> None:
        self.started_at = time.time()

    def finalize(self) -> None:
        self.ended_at = time.time()
        self.total_duration_ms = (self.ended_at - self.started_at) * 1000
        self.total_tests = len(self.results)
        self.passed = sum(1 for r in self.results if r.overall_success)
        self.failed = self.total_tests - self.passed

        # Compute aggregated metrics
        if self.results:
            self.avg_systems_match_ratio = sum(
                r.system_match_ratio for r in self.results
            ) / len(self.results)
            self.avg_files_generated = sum(
                r.files_generated for r in self.results
            ) / len(self.results)
            self.avg_lines_of_code = sum(
                r.total_lines_of_code for r in self.results
            ) / len(self.results)
            genre_matches = sum(1 for r in self.results if r.genre_match)
            self.genre_accuracy = genre_matches / len(self.results)

        # Duration by level
        by_level: dict[str, list[float]] = {}
        for r in self.results:
            by_level.setdefault(r.level, []).append(r.total_duration_ms)
        self.avg_duration_by_level = {
            level: sum(durations) / len(durations)
            for level, durations in by_level.items()
        }

    def add_result(self, result: TestResult) -> None:
        self.results.append(result)


def save_report(summary: TestRunSummary, output_dir: Path) -> Path:
    """Save test run report as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"test_report_{summary.run_id}.json"

    report = {
        "run_id": summary.run_id,
        "started_at": summary.started_at,
        "ended_at": summary.ended_at,
        "total_duration_ms": summary.total_duration_ms,
        "total_tests": summary.total_tests,
        "passed": summary.passed,
        "failed": summary.failed,
        "genre_accuracy": summary.genre_accuracy,
        "avg_systems_match_ratio": summary.avg_systems_match_ratio,
        "avg_files_generated": summary.avg_files_generated,
        "avg_lines_of_code": summary.avg_lines_of_code,
        "avg_duration_by_level": summary.avg_duration_by_level,
        "results": [asdict(r) for r in summary.results],
    }

    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report_path


def format_summary_table(summary: TestRunSummary) -> str:
    """Format summary as a human-readable table."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"  TEST HARNESS REPORT — Run: {summary.run_id}")
    lines.append("=" * 80)
    lines.append(
        f"  Total: {summary.total_tests}  |  "
        f"Passed: {summary.passed}  |  "
        f"Failed: {summary.failed}  |  "
        f"Duration: {summary.total_duration_ms:.0f}ms"
    )
    lines.append("-" * 80)
    lines.append(
        f"  Genre Accuracy:        {summary.genre_accuracy * 100:.1f}%"
    )
    lines.append(
        f"  Avg System Match:      {summary.avg_systems_match_ratio * 100:.1f}%"
    )
    lines.append(
        f"  Avg Files Generated:   {summary.avg_files_generated:.1f}"
    )
    lines.append(
        f"  Avg Lines of Code:     {summary.avg_lines_of_code:.0f}"
    )
    lines.append("-" * 80)

    for level in ("simple", "medium", "full"):
        avg = summary.avg_duration_by_level.get(level)
        if avg is not None:
            lines.append(f"  Avg Duration [{level:>6}]:  {avg:.0f}ms")

    lines.append("-" * 80)
    lines.append("")

    # Per-test results table
    header = f"  {'ID':<25} {'Level':<8} {'Genre':<8} {'Sys%':>5} {'Files':>5} {'LOC':>6} {'ms':>8} {'Status':<6}"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    for r in summary.results:
        status = "PASS" if r.overall_success else "FAIL"
        lines.append(
            f"  {r.prompt_id:<25} {r.level:<8} "
            f"{'✓' if r.genre_match else '✗':<8} "
            f"{r.system_match_ratio * 100:>4.0f}% "
            f"{r.files_generated:>5} "
            f"{r.total_lines_of_code:>6} "
            f"{r.total_duration_ms:>7.0f} "
            f"{status:<6}"
        )

    lines.append("")

    # Show failures detail
    failures = [r for r in summary.results if not r.overall_success]
    if failures:
        lines.append("  FAILURES:")
        lines.append("  " + "-" * 76)
        for r in failures:
            lines.append(f"  [{r.prompt_id}]")
            if not r.genre_match:
                lines.append(
                    f"    Genre mismatch: expected={r.expected_genre}, actual={r.actual_genre}"
                )
            if r.systems_missing:
                lines.append(
                    f"    Missing systems: {', '.join(r.systems_missing)}"
                )
            if not r.files_met_minimum:
                lines.append(
                    f"    Insufficient files: {r.files_generated} < {r.min_files_expected}"
                )
            for err in r.errors:
                lines.append(f"    Error: {err}")
        lines.append("")

    lines.append("=" * 80)
    return "\n".join(lines)
