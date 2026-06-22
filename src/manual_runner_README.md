# `manual_runner.py` Explained

This file is the manual benchmark runner for AI Stress Test Lab.

It is designed for situations where you are testing models through a website or app instead of an API. For example, you can copy a prompt into ChatGPT Plus, paste the answer back into the terminal, manually grade the answer, and save the result.

## What this file does

`manual_runner.py` does the actual manual evaluation process:

```text
load prompt dataset
    ↓
show prompt 1
    ↓
you paste the model answer
    ↓
you mark pass/fail
    ↓
if failed, you enter severity and failure type
    ↓
save the result
    ↓
repeat for every prompt
    ↓
save all results as a JSON file
```

## How to run it

From the root of the repository:

```bash
python src/manual_runner.py --model "ChatGPT Plus"
```

That uses the default dataset:

```text
prompts/easy_v0_1.json
```

and saves results to:

```text
results/manual
```

You can also choose a dataset manually:

```bash
python src/manual_runner.py --model "ChatGPT Plus" --dataset prompts/easy_v0_1.json
```

## Full file

```python
"""Manual benchmark runner for AI Stress Test Lab.

This runner is designed for ChatGPT Plus / web UI usage, where there is no API.
It shows each prompt, lets the evaluator paste a model answer, asks for a manual
pass/fail grade, and saves the results as JSON.
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

        notes = input("Notes: ").strip()

        result = create_result_record(
            prompt=prompt,
            model_name=model_name,
            model_answer=model_answer,
            passed=passed,
            severity=severity,
            failure_types=failure_types,
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
```

## Line-by-line explanation

### Lines 1-7

```python
"""Manual benchmark runner for AI Stress Test Lab.

This runner is designed for ChatGPT Plus / web UI usage, where there is no API.
It shows each prompt, lets the evaluator paste a model answer, asks for a manual
pass/fail grade, and saves the results as JSON.
"""
```

This is the file docstring. It explains the whole file.

It says this runner is for manual use, which means you are not calling an AI model through code yet.

Instead, you use a model through a website or app, paste the answer into the terminal, and grade it yourself.

### Line 9

```python
from __future__ import annotations
```

This helps Python handle type hints cleanly.

You do not need it for the main logic. It is mostly a compatibility and code-quality line.

### Line 11

```python
import argparse
```

This imports Python's command-line argument library.

It lets the script understand arguments like:

```bash
--model "ChatGPT Plus"
```

and:

```bash
--dataset prompts/easy_v0_1.json
```

### Line 12

```python
import json
```

This imports Python's JSON library.

This file needs JSON because:

- the prompt dataset is stored as JSON
- the result file is saved as JSON

So `json` is used for reading and writing structured data.

### Line 13

```python
from datetime import datetime, timezone
```

This imports tools for working with dates and times.

The script uses this to create timestamps for result files.

Example timestamp format:

```text
20260622_124736
```

### Line 14

```python
from pathlib import Path
```

This imports `Path`, which is a clean way to work with file paths.

Instead of treating paths as basic strings, Python can treat them as path objects.

Example:

```python
Path("results/manual")
```

### Line 15

```python
from typing import Any
```

This imports `Any`, a type hint.

`Any` means a value can be any type.

In this file, it appears in types like:

```python
dict[str, Any]
```

That means:

```text
A dictionary with string keys, and values that can be any type.
```

That is useful because prompt records contain strings, lists, booleans, and other values.

### Lines 17-22

```python
from scorer import (
    VALID_FAILURE_TYPES,
    VALID_SEVERITIES,
    create_result_record,
    parse_failure_types,
)
```

This imports values and functions from `scorer.py`.

| Imported item | Purpose |
|---|---|
| `VALID_FAILURE_TYPES` | List of allowed failure type names |
| `VALID_SEVERITIES` | List of allowed severity values |
| `create_result_record` | Builds one clean result dictionary |
| `parse_failure_types` | Converts comma-separated text into a list |

This is important because `manual_runner.py` handles the user interaction, while `scorer.py` handles grading structure and validation.

### Line 25

```python
DEFAULT_DATASET = "prompts/easy_v0_1.json"
```

This defines the default prompt dataset.

If you run the script without choosing a dataset, it will use:

```text
prompts/easy_v0_1.json
```

### Line 26

```python
DEFAULT_OUTPUT_DIR = "results/manual"
```

This defines the default output folder.

If you do not choose another output folder, results will be saved under:

```text
results/manual
```

## `load_prompts`

### Line 29

```python
def load_prompts(dataset_path: Path) -> list[dict[str, Any]]:
```

This defines a function named `load_prompts`.

Its job is to load the prompt dataset from a JSON file.

The input is:

```python
dataset_path: Path
```

That means the function expects a file path.

The return type is:

```python
list[dict[str, Any]]
```

That means it returns a list of dictionaries. Each dictionary is one prompt record.

### Line 30

```python
    """Load prompts from a JSON dataset file."""
```

This is the function docstring.

It says what the function does.

### Lines 31-32

```python
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
```

This checks if the dataset file exists.

If it does not exist, the script stops and raises a clear error.

This prevents confusing errors later.

### Lines 34-35

```python
    with dataset_path.open("r", encoding="utf-8") as file:
```

This opens the dataset file.

Parts:

| Code | Meaning |
|---|---|
| `dataset_path.open(...)` | Open the file |
| `"r"` | Read mode |
| `encoding="utf-8"` | Read text using UTF-8 encoding |
| `as file` | Store the opened file object in a variable named `file` |

The `with` statement automatically closes the file after Python finishes reading it.

### Line 36

```python
        prompts = json.load(file)
```

This reads the JSON file and converts it into Python data.

The JSON list becomes a Python list.

Each JSON object becomes a Python dictionary.

### Lines 38-39

```python
    if not isinstance(prompts, list):
        raise ValueError("Dataset must be a JSON list of prompt objects.")
```

This checks that the loaded JSON is a list.

The dataset should look like:

```json
[
  { "id": "E001", "prompt": "..." },
  { "id": "E002", "prompt": "..." }
]
```

If the dataset is not a list, the script stops with a clear error.

### Line 41

```python
    return prompts
```

This returns the loaded prompts so the rest of the program can use them.

## `read_multiline_answer`

### Line 44

```python
def read_multiline_answer() -> str:
```

This defines a function named `read_multiline_answer`.

It returns a string.

Its job is to let you paste a model's answer, even if the answer has multiple lines.

### Line 45

```python
    """Read a pasted model answer until the evaluator types END on its own line."""
```

This docstring explains the function.

You paste the model answer, then type:

```text
END
```

on its own line to finish.

### Lines 46-47

```python
    print("Paste the model answer below.")
    print("Type END on its own line when finished.\n")
```

These print instructions to the terminal.

The `\n` adds an extra blank line.

### Line 49

```python
    lines: list[str] = []
```

This creates an empty list named `lines`.

The type hint `list[str]` means it should store strings.

Each line you paste gets added to this list.

### Line 50

```python
    while True:
```

This starts an infinite loop.

It keeps asking for input until something inside the loop breaks it.

### Line 51

```python
        line = input()
```

This reads one line of text from the terminal.

Whatever you type becomes the value of `line`.

### Lines 52-53

```python
        if line.strip() == "END":
            break
```

This checks if the line is exactly `END` after removing extra spaces.

If it is, the loop stops.

`break` means exit the nearest loop.

### Line 54

```python
        lines.append(line)
```

If the line was not `END`, this adds it to the `lines` list.

### Line 56

```python
    return "\n".join(lines).strip()
```

This combines all pasted lines into one string.

`"\n".join(lines)` joins the lines with newline characters between them.

`.strip()` removes extra blank space from the beginning and end.

Then the full pasted answer is returned.

## `ask_yes_no`

### Line 59

```python
def ask_yes_no(question: str) -> bool:
```

This defines a function that asks a yes/no question.

It takes one input:

```python
question: str
```

and returns:

```python
bool
```

A boolean is either `True` or `False`.

### Line 60

```python
    """Ask a yes/no question and return True for yes."""
```

This docstring explains the function.

### Line 61

```python
    while True:
```

This starts a loop that keeps running until the user enters a valid answer.

### Line 62

```python
        answer = input(f"{question} [y/n]: ").strip().lower()
```

This shows the question and reads the user's answer.

Parts:

| Code | Meaning |
|---|---|
| `input(...)` | Get text from the user |
| `f"{question} [y/n]: "` | Insert the question into the prompt text |
| `.strip()` | Remove extra spaces |
| `.lower()` | Convert to lowercase |

So `YES`, `Yes`, and `yes` all become `yes`.

### Lines 63-64

```python
        if answer in {"y", "yes"}:
            return True
```

If the answer is `y` or `yes`, return `True`.

### Lines 65-66

```python
        if answer in {"n", "no"}:
            return False
```

If the answer is `n` or `no`, return `False`.

### Line 67

```python
        print("Please enter y or n.")
```

If the answer was not valid, print a correction message and loop again.

## `ask_failure_metadata`

### Line 70

```python
def ask_failure_metadata() -> tuple[str, list[str]]:
```

This defines a function used only when the model fails a prompt.

It returns two things:

```python
tuple[str, list[str]]
```

That means:

```text
severity as a string
failure types as a list of strings
```

### Line 71

```python
    """Ask for severity and failure types after a failed response."""
```

This docstring explains the function.

### Lines 72-73

```python
    print("\nValid severities:")
    print(", ".join(VALID_SEVERITIES))
```

These lines print the allowed severity values.

`", ".join(VALID_SEVERITIES)` combines the list into one readable line separated by commas.

### Lines 75-79

```python
    while True:
        severity = input("Severity: ").strip().lower()
        if severity in VALID_SEVERITIES:
            break
        print("Invalid severity. Try again.")
```

This repeatedly asks for a severity until the user enters a valid one.

If the entered severity is in `VALID_SEVERITIES`, the loop ends.

Otherwise, the script asks again.

### Lines 81-82

```python
    print("\nValid failure types:")
    print(", ".join(VALID_FAILURE_TYPES))
```

These print the allowed failure types.

### Line 83

```python
    raw_failure_types = input("Failure types, comma-separated: ")
```

This asks the user to enter failure types separated by commas.

Example:

```text
hallucination, calibration_failure
```

### Line 84

```python
    failure_types = parse_failure_types(raw_failure_types)
```

This calls `parse_failure_types` from `scorer.py`.

It converts the comma-separated text into a Python list.

Example:

```text
hallucination, calibration_failure
```

becomes:

```python
["hallucination", "calibration_failure"]
```

### Line 86

```python
    return severity, failure_types
```

This returns both pieces of failure information.

## `display_prompt`

### Line 89

```python
def display_prompt(prompt: dict[str, Any], index: int, total: int) -> None:
```

This defines a function that prints one prompt to the terminal.

Inputs:

| Input | Meaning |
|---|---|
| `prompt` | The prompt dictionary |
| `index` | Which prompt number this is |
| `total` | How many prompts are in the dataset |

It returns `None`, meaning it only prints information and does not return a value.

### Line 90

```python
    """Print one prompt and its grading information."""
```

This docstring explains the function.

### Line 91

```python
    print("\n" + "=" * 80)
```

This prints a blank line and then 80 equals signs.

`"=" * 80` means repeat `=` 80 times.

This makes a visual divider in the terminal.

### Line 92

```python
    print(f"Prompt {index}/{total}: {prompt.get('id', 'unknown')}")
```

This prints something like:

```text
Prompt 1/10: E001
```

`prompt.get('id', 'unknown')` means:

- get the prompt's `id`
- if there is no `id`, use `unknown`

### Line 93

```python
    print("=" * 80)
```

This prints another divider line.

### Lines 94-97

```python
    print(f"Category:   {prompt.get('category')}")
    print(f"Difficulty: {prompt.get('difficulty')}")
    print(f"Risk:       {prompt.get('risk')}")
    print(f"Domain:     {prompt.get('domain')}")
```

These print prompt metadata.

This helps you grade with context.

### Lines 98-99

```python
    print("\nPROMPT:")
    print(prompt.get("prompt", ""))
```

These print the actual prompt text.

If the prompt field is missing, it prints an empty string.

### Lines 100-103

```python
    print("\nEXPECTED BEHAVIOR:")
    print(prompt.get("expected_behavior", ""))
    print("\nFAILURE CONDITION:")
    print(prompt.get("failure_condition", ""))
```

These print the grading guide.

This tells you what should count as success or failure.

### Line 104

```python
    print("=" * 80 + "\n")
```

This prints one final divider and a blank line.

## `save_results`

### Lines 107-112

```python
def save_results(
    output_dir: Path,
    dataset_path: Path,
    model_name: str,
    results: list[dict[str, Any]],
) -> Path:
```

This defines a function that saves the benchmark results.

Inputs:

| Input | Meaning |
|---|---|
| `output_dir` | Folder where results should be saved |
| `dataset_path` | Dataset that was used |
| `model_name` | Name of the model tested |
| `results` | List of result records |

It returns a `Path`, which is the path to the saved results file.

### Line 113

```python
    """Save a benchmark run to a timestamped JSON file."""
```

This docstring explains the function.

### Line 114

```python
    output_dir.mkdir(parents=True, exist_ok=True)
```

This creates the output folder if it does not already exist.

Parts:

| Code | Meaning |
|---|---|
| `parents=True` | Create parent folders too if needed |
| `exist_ok=True` | Do not crash if the folder already exists |

### Line 116

```python
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
```

This creates a timestamp using the current UTC time.

Example:

```text
20260622_124736
```

The timestamp helps make each result file unique.

### Line 117

```python
    safe_model_name = model_name.lower().replace(" ", "_").replace("/", "_")
```

This turns the model name into something safer for a filename.

Example:

```text
ChatGPT Plus
```

becomes:

```text
chatgpt_plus
```

It also replaces `/` with `_` because slashes can confuse file paths.

### Line 118

```python
    output_path = output_dir / f"{timestamp}_{safe_model_name}.json"
```

This builds the final output file path.

Example:

```text
results/manual/20260622_124736_chatgpt_plus.json
```

The `/` operator is special for `Path` objects. It joins folders and filenames.

### Lines 120-129

```python
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
```

This creates the final dictionary that will be saved as JSON.

Fields:

| Field | Meaning |
|---|---|
| `run_id` | Timestamp ID for the run |
| `model` | Model name |
| `dataset` | Dataset path |
| `created_at` | Full timestamp |
| `total_prompts` | Number of prompts tested |
| `passed` | Number of passing responses |
| `failed` | Number of failing responses |
| `results` | Full list of per-prompt results |

This part:

```python
sum(1 for result in results if result["passed"])
```

counts how many results passed.

This part:

```python
sum(1 for result in results if not result["passed"])
```

counts how many failed.

### Lines 131-132

```python
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(run_record, file, indent=2)
```

This opens the output file in write mode and saves the `run_record` dictionary as JSON.

Parts:

| Code | Meaning |
|---|---|
| `"w"` | Write mode |
| `encoding="utf-8"` | Use UTF-8 text encoding |
| `json.dump(...)` | Write Python data as JSON |
| `indent=2` | Make the JSON readable with spacing |

### Line 134

```python
    return output_path
```

This returns the path to the saved result file.

## `run_manual_benchmark`

### Lines 137-141

```python
def run_manual_benchmark(
    dataset_path: Path,
    model_name: str,
    output_dir: Path,
) -> Path:
```

This defines the main function for running a full manual benchmark.

Inputs:

| Input | Meaning |
|---|---|
| `dataset_path` | Prompt dataset to load |
| `model_name` | Model being tested |
| `output_dir` | Where results are saved |

It returns the saved result file path.

### Line 142

```python
    """Run a full manual benchmark session."""
```

This docstring explains the function.

### Line 143

```python
    prompts = load_prompts(dataset_path)
```

This loads the prompt dataset using the `load_prompts` function.

Now `prompts` is a list of prompt dictionaries.

### Line 144

```python
    results: list[dict[str, Any]] = []
```

This creates an empty list to store results.

Each prompt will add one result dictionary to this list.

### Line 146

```python
    for index, prompt in enumerate(prompts, start=1):
```

This loops through every prompt.

`enumerate(prompts, start=1)` gives two things each time:

| Variable | Meaning |
|---|---|
| `index` | Prompt number, starting at 1 |
| `prompt` | The actual prompt dictionary |

### Line 147

```python
        display_prompt(prompt, index, len(prompts))
```

This shows the current prompt in the terminal.

`len(prompts)` gives the total number of prompts.

### Line 148

```python
        model_answer = read_multiline_answer()
```

This asks you to paste the model's answer.

The pasted answer is stored in `model_answer`.

### Line 150

```python
        passed = ask_yes_no("Did the model pass this prompt?")
```

This asks whether the model passed.

The answer becomes a boolean:

```python
True
```

or:

```python
False
```

### Lines 152-156

```python
        if passed:
            severity = None
            failure_types: list[str] = []
        else:
            severity, failure_types = ask_failure_metadata()
```

If the model passed:

- severity is `None`
- failure types is an empty list

If the model failed:

- ask for severity
- ask for failure types

### Line 158

```python
        notes = input("Notes: ").strip()
```

This asks you to type notes about the result.

`.strip()` removes extra space at the beginning and end.

### Lines 160-168

```python
        result = create_result_record(
            prompt=prompt,
            model_name=model_name,
            model_answer=model_answer,
            passed=passed,
            severity=severity,
            failure_types=failure_types,
            notes=notes,
        )
```

This creates one clean result record.

It calls `create_result_record` from `scorer.py`.

That function also checks whether your grading data is valid.

Example: if the model failed, it makes sure severity and failure type are provided.

### Line 169

```python
        results.append(result)
```

This adds the result record to the results list.

### Lines 171-176

```python
    return save_results(
        output_dir=output_dir,
        dataset_path=dataset_path,
        model_name=model_name,
        results=results,
    )
```

After all prompts are done, this saves the full benchmark run.

It returns the output path from `save_results`.

## `parse_args`

### Line 179

```python
def parse_args() -> argparse.Namespace:
```

This defines a function for reading command-line options.

It returns an `argparse.Namespace`, which stores the parsed arguments.

### Line 180

```python
    """Parse command-line arguments."""
```

This docstring explains the function.

### Line 181

```python
    parser = argparse.ArgumentParser(description="Run a manual AI stress-test benchmark.")
```

This creates the argument parser.

The description appears when someone runs:

```bash
python src/manual_runner.py --help
```

### Line 182

```python
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to prompt dataset JSON.")
```

This adds the optional `--dataset` argument.

If not provided, it uses `DEFAULT_DATASET`.

### Line 183

```python
    parser.add_argument("--model", required=True, help="Name of the model being tested.")
```

This adds the required `--model` argument.

The user must provide a model name.

### Line 184

```python
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for results.")
```

This adds the optional `--output-dir` argument.

If not provided, it uses `DEFAULT_OUTPUT_DIR`.

### Line 185

```python
    return parser.parse_args()
```

This reads the command-line arguments and returns them.

## `main`

### Line 188

```python
def main() -> None:
```

This defines the main function for the file.

It returns `None`, meaning it runs actions but does not return a useful value.

### Line 189

```python
    """CLI entry point."""
```

This docstring says this is where the command-line version starts.

### Line 190

```python
    args = parse_args()
```

This reads the command-line arguments.

After this, the script knows:

```text
args.dataset
args.model
args.output_dir
```

### Lines 191-195

```python
    output_path = run_manual_benchmark(
        dataset_path=Path(args.dataset),
        model_name=args.model,
        output_dir=Path(args.output_dir),
    )
```

This runs the full manual benchmark.

It passes the dataset path, model name, and output folder into `run_manual_benchmark`.

The returned result file path is stored in `output_path`.

### Line 196

```python
    print(f"\nSaved results to {output_path}")
```

This prints the saved result location.

The `f` makes it an f-string, so `{output_path}` gets replaced with the actual result path.

### Line 199

```python
if __name__ == "__main__":
```

This checks whether the file is being run directly.

If you run:

```bash
python src/manual_runner.py --model "ChatGPT Plus"
```

then the condition is true.

### Line 200

```python
    main()
```

This calls the `main` function.

That starts the script.

## Mental model

Think of `manual_runner.py` as the person running the experiment.

It says:

```text
Here is the prompt.
Paste the model answer.
Did it pass?
If it failed, how bad was it?
What kind of failure was it?
Any notes?
Okay, I saved it.
```

## What this file does not do yet

This file does not:

- call OpenAI, Anthropic, Gemini, or any other API
- automatically grade answers
- generate Markdown reports
- compare multiple models automatically
- create charts

It is intentionally the first simple version: manual testing and manual grading.
