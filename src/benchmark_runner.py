"""Top-level benchmark runner for AI Stress Test Lab.

For now, this file supports manual mode only. Later, it can become the main
entry point for API-based model runs, automatic grading, and report generation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from manual_runner import DEFAULT_DATASET, DEFAULT_OUTPUT_DIR, run_manual_benchmark


SUPPORTED_MODES = ["manual"]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run AI Stress Test Lab benchmarks.")
    parser.add_argument(
        "--mode",
        default="manual",
        choices=SUPPORTED_MODES,
        help="Benchmark mode. Currently only manual mode is supported.",
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to prompt dataset JSON.")
    parser.add_argument("--model", required=True, help="Name of the model being tested.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for results.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()

    if args.mode == "manual":
        output_path = run_manual_benchmark(
            dataset_path=Path(args.dataset),
            model_name=args.model,
            output_dir=Path(args.output_dir),
        )
        print(f"\nSaved results to {output_path}")
        return

    raise ValueError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()
