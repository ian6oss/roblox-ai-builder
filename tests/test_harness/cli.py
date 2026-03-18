#!/usr/bin/env python3
"""CLI test harness for systematic prompt-to-code generation testing.

Usage:
    python -m tests.test_harness.cli [OPTIONS]

Examples:
    # Run all tests (no AI, uses fallback generation)
    python -m tests.test_harness.cli

    # Run only simple prompts
    python -m tests.test_harness.cli --level simple

    # Run with AI (requires ANTHROPIC_API_KEY)
    python -m tests.test_harness.cli --use-ai

    # Run a single test by ID
    python -m tests.test_harness.cli --test-id simple-obby-01

    # Save results to custom directory
    python -m tests.test_harness.cli --output-dir ./test_results

    # Run without writing files to disk
    python -m tests.test_harness.cli --no-write

    # Verbose mode with per-stage details
    python -m tests.test_harness.cli --verbose
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.test_harness.metrics import (
    TestRunSummary,
    format_summary_table,
    save_report,
)
from tests.test_harness.runner import TestRunner
from tests.test_harness.test_prompts import ALL_PROMPTS, TestPrompt, get_prompts_by_level


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI test harness for Roblox AI Builder prompt-to-code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--level",
        choices=["simple", "medium", "full", "all"],
        default="all",
        help="Complexity level to test (default: all)",
    )
    parser.add_argument(
        "--test-id",
        type=str,
        default=None,
        help="Run a specific test by ID",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Use Claude API for generation (requires ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for test output files (default: ./test_output)",
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        default=None,
        help="Directory for test reports (default: ./test_reports)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Skip writing generated files to disk",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose per-stage output",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON report (no table)",
    )
    return parser.parse_args()


async def run_test_suite(
    prompts: list[TestPrompt],
    ai_client=None,
    output_dir: Path | None = None,
    write_to_disk: bool = True,
    verbose: bool = False,
) -> TestRunSummary:
    """Run a suite of test prompts and collect results."""
    run_id = f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    summary = TestRunSummary(run_id=run_id)
    summary.start()

    runner = TestRunner(
        ai_client=ai_client,
        output_dir=output_dir,
        write_to_disk=write_to_disk,
    )

    total = len(prompts)
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{total}] Running: {prompt.id} ({prompt.level})")
        print(f"  Prompt: {prompt.prompt[:80]}{'...' if len(prompt.prompt) > 80 else ''}")

        result = await runner.run(prompt)
        summary.add_result(result)

        # Print per-test summary
        status = "✓ PASS" if result.overall_success else "✗ FAIL"
        print(f"  {status}  |  {result.total_duration_ms:.0f}ms  |  "
              f"Files: {result.files_generated}  |  LOC: {result.total_lines_of_code}  |  "
              f"Genre: {'✓' if result.genre_match else '✗'}  |  "
              f"Systems: {result.system_match_ratio * 100:.0f}%")

        if verbose:
            for stage in result.stages:
                s_status = "✓" if stage.success else "✗"
                print(f"    [{s_status}] {stage.stage}: {stage.duration_ms:.0f}ms")
                if stage.error:
                    print(f"        Error: {stage.error}")
                if stage.output_summary:
                    for k, v in stage.output_summary.items():
                        val_str = str(v)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        print(f"        {k}: {val_str}")

        if result.errors and not result.overall_success:
            for err in result.errors:
                err_short = err.split("\n")[0]
                print(f"  ⚠ {err_short}")

    summary.finalize()
    return summary


def main() -> None:
    args = parse_args()

    # Select prompts
    if args.test_id:
        prompts = [p for p in ALL_PROMPTS if p.id == args.test_id]
        if not prompts:
            print(f"Error: test ID '{args.test_id}' not found.")
            print("Available IDs:")
            for p in ALL_PROMPTS:
                print(f"  {p.id} ({p.level}): {p.description}")
            sys.exit(1)
    else:
        prompts = get_prompts_by_level(args.level)

    print(f"Roblox AI Builder — Test Harness")
    print(f"Level: {args.level}  |  Tests: {len(prompts)}  |  AI: {'Yes' if args.use_ai else 'No (fallback)'}")
    print("=" * 60)

    # Setup AI client if requested
    ai_client = None
    if args.use_ai:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: --use-ai requires ANTHROPIC_API_KEY environment variable")
            sys.exit(1)
        from roblox_ai_builder.utils.ai_client import AIClient
        ai_client = AIClient(api_key=api_key)

    # Setup output directories
    base_dir = Path(args.output_dir) if args.output_dir else Path("test_output")
    report_dir = Path(args.report_dir) if args.report_dir else Path("test_reports")

    # Run tests
    summary = asyncio.run(
        run_test_suite(
            prompts=prompts,
            ai_client=ai_client,
            output_dir=base_dir,
            write_to_disk=not args.no_write,
            verbose=args.verbose,
        )
    )

    # Save report
    report_path = save_report(summary, report_dir)
    print(f"\nReport saved: {report_path}")

    # Print summary
    if not args.json_only:
        print()
        print(format_summary_table(summary))

    # Exit with non-zero if any tests failed
    sys.exit(0 if summary.failed == 0 else 1)


if __name__ == "__main__":
    main()
