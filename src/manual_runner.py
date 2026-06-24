"""Manual benchmark runner for AI Stress Test Lab.

This runner is designed for ChatGPT Plus / web UI usage, where there is no API.
It shows each prompt, lets the evaluator paste a model answer, asks for a manual
pass/fail grade, asks for an optional numeric quality rating, and saves the results as JSON.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scorer import (
    VALID_FAILURE_TYPES,
    VALID_SEVERITIES,
    create_result_record,
    parse_failure_types,
)


DEFAULT_DATASET = "prompts/easy_v0_1.json"
DEFAULT_OUTPUT_DIR = "results/manual"


def load_prompts(dataset_path: Path) -> list[dict[str, Any]]:
    """Load prompts from a JSON dataset file."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        prompts = json.load(file)

    if not isinstance(prompts, list):
        raise ValueError("Dataset must be a JSON list of prompt objects.")

    return prompts


def read_multiline_answer() -> str:
    """Read a pasted model answer until the evaluator types END on its own line."""
    print("Paste the model answer below.")
    print("Type END on its own line when finished.\n")

    lines: list[str] = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines).strip()


def ask_yes_no(question: str) -> bool:
    """Ask a yes/no question and return True for yes."""
    while True:
        answer = input(f"{question} [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please enter y or n.")


def ask_failure_metadata() -> tuple[str, list[str]]:
    """Ask for severity and failure types after a failed response."""
    print("\nValid severities:")
    print(", ".join(VALID_SEVERITIES))

    while True:
        severity = input("Severity: ").strip().lower()
        if severity in VALID_SEVERITIES:
            break
        print("Invalid severity. Try again.")

    print("\nValid failure types:")
    print(", ".join(VALID_FAILURE_TYPES))
    raw_failure_types = input("Failure types, comma-separated: ")
    failure_types = parse_failure_types(raw_failure_types)

    return severity, failure_types


def ask_quality_value() -> int | None:
    """Ask for an optional numeric quality rating from 0 to 100."""
    while True:
        raw_quality = input("Quality (0-100, optional): ").strip()
        if raw_quality == "":
            return None
        if raw_quality.isdigit():
            quality = int(raw_quality)
            if 0 <= quality <= 100:
                return quality
        print("Please enter a number between 0 and 100, or leave blank.")


def display_prompt(prompt: dict[str, Any], index: int, total: int) -> None:
    """Print one prompt and its grading information."""
    print("\n" + "=" * 80)
    print(f"Prompt {index}/{total}: {prompt.get('id', 'unknown')}")
    print("=" * 80)
    print(f"Category:   {prompt.get('category')}")
    print(f"Difficulty: {prompt.get('difficulty')}")
    print(f"Risk:       {prompt.get('risk')}")
    print(f"Domain:     {prompt.get('domain')}")
    print("\nPROMPT:")
    print(prompt.get("prompt", ""))
    print("\nEXPECTED BEHAVIOR:")
    print(prompt.get("expected_behavior", ""))
    print("\nFAILURE CONDITION:")
    print(prompt.get("failure_condition", ""))
    print("=" * 80 + "\n")


def save_results(
    output_dir: Path,
    dataset_path: Path,
    model_name: str,
    results: list[dict[str, Any]],
) -> Path:
    """Save a benchmark run to a timestamped JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_model_name = model_name.lower().replace(" ", "_").replace("/", "_")
    output_path = output_dir / f"{timestamp}_{safe_model_name}.json"

    run_record = {
        "run_id": timestamp,
        "model": model_name,
        "dataset": str(dataset_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_prompts": len(results),
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(run_record, file, indent=2)

    return output_path


def run_manual_benchmark(
    dataset_path: Path,
    model_name: str,
    output_dir: Path,
) -> Path:
    """Run a full manual benchmark session."""
    prompts = load_prompts(dataset_path)
    results: list[dict[str, Any]] = []

    for index, prompt in enumerate(prompts, start=1):
        display_prompt(prompt, index, len(prompts))
        model_answer = read_multiline_answer()

        passed = ask_yes_no("Did the model pass this prompt?")

        if passed:
            severity = None
            failure_types: list[str] = []
        else:
            severity, failure_types = ask_failure_metadata()

        quality = ask_quality_value()
        notes = input("Notes: ").strip()

        result = create_result_record(
            prompt=prompt,
            model_name=model_name,
            model_answer=model_answer,
            passed=passed,
            severity=severity,
            failure_types=failure_types,
            quality=quality,
            notes=notes,
        )
        results.append(result)

    return save_results(
        output_dir=output_dir,
        dataset_path=dataset_path,
        model_name=model_name,
        results=results,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run a manual AI stress-test benchmark.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to prompt dataset JSON.")
    parser.add_argument("--model", required=True, help="Name of the model being tested.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for results.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    output_path = run_manual_benchmark(
        dataset_path=Path(args.dataset),
        model_name=args.model,
        output_dir=Path(args.output_dir),
    )
    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
