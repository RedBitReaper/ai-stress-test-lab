# `benchmark_runner.py` Explained

This file is the top-level command-line launcher for AI Stress Test Lab.

It does not contain the full benchmark logic by itself. Instead, it reads command-line options and then calls the correct runner. Right now, the only supported runner is manual mode.

## How to run it

From the root of the repository:

```bash
python src/benchmark_runner.py --model "ChatGPT Plus"
```

This uses the defaults:

- mode: `manual`
- dataset: `prompts/easy_v0_1.json`
- output directory: `results/manual`

You can also write the full version:

```bash
python src/benchmark_runner.py --mode manual --dataset prompts/easy_v0_1.json --model "ChatGPT Plus" --output-dir results/manual
```

## Full file

```python
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
```

## Big picture

The file works like this:

```text
terminal command
    ↓
benchmark_runner.py
    ↓
read arguments like --model and --dataset
    ↓
if mode is manual, call manual_runner.py
    ↓
save the result file path
    ↓
print where the results were saved
```

## Line-by-line explanation

### Lines 1-5

```python
"""Top-level benchmark runner for AI Stress Test Lab.

For now, this file supports manual mode only. Later, it can become the main
entry point for API-based model runs, automatic grading, and report generation.
"""
```

This is a docstring.

A docstring is a text explanation inside triple quotes. Python does not treat it like normal code. It is used to explain what a file, function, or class does.

This docstring says:

- this file is the top-level benchmark runner
- right now it only supports manual mode
- later it can support API runs, automatic grading, and report generation

### Line 7

```python
from __future__ import annotations
```

This imports a future Python feature.

For this project, the simple explanation is:

- it helps Python handle type hints more smoothly
- type hints are labels that describe what kind of value something should be
- it is not directly part of the benchmark logic

Example of a type hint from later in the file:

```python
def main() -> None:
```

The `-> None` part means the function is not supposed to return a value.

### Line 9

```python
import argparse
```

This imports Python's built-in `argparse` module.

`argparse` lets this file understand terminal arguments.

For example, in this command:

```bash
python src/benchmark_runner.py --model "ChatGPT Plus"
```

`argparse` is what lets Python read:

```text
model = ChatGPT Plus
```

Without `argparse`, the script would not know what `--model` means.

### Line 10

```python
from pathlib import Path
```

This imports `Path` from Python's built-in `pathlib` module.

`Path` is used for file and folder paths.

Instead of treating this as just a string:

```python
"prompts/easy_v0_1.json"
```

we can convert it into a path object:

```python
Path("prompts/easy_v0_1.json")
```

That makes it easier and safer for Python to work with files.

### Line 12

```python
from manual_runner import DEFAULT_DATASET, DEFAULT_OUTPUT_DIR, run_manual_benchmark
```

This imports three things from `manual_runner.py`.

This means `benchmark_runner.py` is borrowing code and values from another file.

The imported items are:

| Name | What it means |
|---|---|
| `DEFAULT_DATASET` | The default prompt file to use |
| `DEFAULT_OUTPUT_DIR` | The default folder where results are saved |
| `run_manual_benchmark` | The function that actually runs the manual benchmark |

So `benchmark_runner.py` is not doing all the work itself. It delegates the real prompt-running process to `manual_runner.py`.

### Line 15

```python
SUPPORTED_MODES = ["manual"]
```

This creates a variable named `SUPPORTED_MODES`.

A variable stores a value.

Here, the value is a list:

```python
["manual"]
```

A list stores multiple values. Right now, the list only has one item: `manual`.

This means the only allowed benchmark mode right now is manual mode.

Later, this could become:

```python
SUPPORTED_MODES = ["manual", "api", "auto-grade", "report"]
```

That would mean the benchmark system supports more ways of running.

### Line 18

```python
def parse_args() -> argparse.Namespace:
```

This defines a function named `parse_args`.

A function is a reusable block of code.

The job of this function is to read terminal arguments.

The `-> argparse.Namespace` part is a type hint. It means this function returns an `argparse.Namespace` object.

An `argparse.Namespace` is basically a container that stores the command-line options after Python reads them.

Example:

```text
args.mode = manual
args.model = ChatGPT Plus
args.dataset = prompts/easy_v0_1.json
args.output_dir = results/manual
```

### Line 19

```python
    """Parse command-line arguments."""
```

This is a function docstring.

It explains what the `parse_args` function does.

The function's job is to parse, or read, command-line arguments.

### Line 20

```python
    parser = argparse.ArgumentParser(description="Run AI Stress Test Lab benchmarks.")
```

This creates an `ArgumentParser` object and stores it in a variable called `parser`.

The parser is the object that knows how to read command-line options like:

```text
--mode
--dataset
--model
--output-dir
```

The `description` text shows up when someone runs:

```bash
python src/benchmark_runner.py --help
```

### Lines 21-27

```python
    parser.add_argument(
        "--mode",
        default="manual",
        choices=SUPPORTED_MODES,
        help="Benchmark mode. Currently only manual mode is supported.",
    )
```

This adds a command-line option called `--mode`.

That means the user can run:

```bash
python src/benchmark_runner.py --mode manual --model "ChatGPT Plus"
```

Each part matters:

| Code | Meaning |
|---|---|
| `"--mode"` | The command-line option name |
| `default="manual"` | Use manual mode if the user does not specify a mode |
| `choices=SUPPORTED_MODES` | Only allow values from `SUPPORTED_MODES` |
| `help=...` | Text shown in the help menu |

Because `SUPPORTED_MODES = ["manual"]`, the only accepted value right now is:

```text
manual
```

### Line 28

```python
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Path to prompt dataset JSON.")
```

This adds a command-line option called `--dataset`.

It lets the user choose which prompt dataset file to run.

If the user does not choose one, it uses:

```python
DEFAULT_DATASET
```

That value comes from `manual_runner.py`.

Right now, the default dataset is expected to be:

```text
prompts/easy_v0_1.json
```

Example custom usage:

```bash
python src/benchmark_runner.py --model "ChatGPT Plus" --dataset prompts/moderate_v0_1.json
```

### Line 29

```python
    parser.add_argument("--model", required=True, help="Name of the model being tested.")
```

This adds a command-line option called `--model`.

The `required=True` part means the user must provide this option.

This command is valid:

```bash
python src/benchmark_runner.py --model "ChatGPT Plus"
```

This command is not valid:

```bash
python src/benchmark_runner.py
```

The model name is saved in the results file so future-you knows which model was tested.

### Line 30

```python
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for results.")
```

This adds a command-line option called `--output-dir`.

It controls where the results file gets saved.

If the user does not provide it, the script uses:

```python
DEFAULT_OUTPUT_DIR
```

That value comes from `manual_runner.py`.

Right now, the default output folder is expected to be:

```text
results/manual
```

### Line 31

```python
    return parser.parse_args()
```

This tells the parser to actually read the command-line arguments.

Then it returns the parsed arguments.

Example command:

```bash
python src/benchmark_runner.py --mode manual --model "ChatGPT Plus"
```

After this line, Python has an object similar to:

```text
args.mode = manual
args.model = ChatGPT Plus
args.dataset = prompts/easy_v0_1.json
args.output_dir = results/manual
```

### Line 34

```python
def main() -> None:
```

This defines a function named `main`.

`main` is the main entry point for the script.

The `-> None` type hint means this function is not intended to return a value.

It performs actions instead:

- reads arguments
- runs the benchmark
- prints where results were saved

### Line 35

```python
    """CLI entry point."""
```

This is the docstring for `main`.

`CLI` means command-line interface.

So this means:

```text
This function is where the command-line version of the program starts.
```

### Line 36

```python
    args = parse_args()
```

This calls the `parse_args` function.

The returned arguments are stored in the variable `args`.

After this line, the program knows the user's settings:

```text
args.mode
args.dataset
args.model
args.output_dir
```

### Line 38

```python
    if args.mode == "manual":
```

This is an `if` statement.

It checks whether the selected mode is manual.

If the condition is true, the indented code under it runs.

Because manual is currently the only supported mode, this is the normal path.

### Lines 39-43

```python
        output_path = run_manual_benchmark(
            dataset_path=Path(args.dataset),
            model_name=args.model,
            output_dir=Path(args.output_dir),
        )
```

This calls the `run_manual_benchmark` function imported from `manual_runner.py`.

This is where the actual benchmark process begins.

It passes three named arguments:

| Argument | Meaning |
|---|---|
| `dataset_path=Path(args.dataset)` | Which JSON prompt file to load |
| `model_name=args.model` | The name of the model being tested |
| `output_dir=Path(args.output_dir)` | Where to save the results |

`Path(args.dataset)` converts the dataset string into a path object.

`Path(args.output_dir)` converts the output folder string into a path object.

The function returns the path to the saved results file.

That returned path is stored in:

```python
output_path
```

### Line 44

```python
        print(f"\nSaved results to {output_path}")
```

This prints the saved result location.

The `f` before the quote makes it an f-string.

An f-string lets Python insert variable values inside `{}`.

Example:

```python
name = "Travis"
print(f"Hello {name}")
```

prints:

```text
Hello Travis
```

In this file, the f-string inserts `output_path` into the message.

The `\n` means newline, so the message starts on a fresh line.

### Line 45

```python
        return
```

This exits the `main` function.

It means:

```text
Manual mode finished successfully, so stop here.
```

### Line 47

```python
    raise ValueError(f"Unsupported mode: {args.mode}")
```

This raises an error if the mode is not supported.

Right now, this line probably will not run because `argparse` already restricts the mode to `SUPPORTED_MODES`.

Still, it is useful defensive programming.

It means:

```text
If an unsupported mode somehow gets here, stop the program and explain the problem.
```

### Line 50

```python
if __name__ == "__main__":
```

This is a common Python pattern.

It checks whether this file is being run directly.

If you run:

```bash
python src/benchmark_runner.py --model "ChatGPT Plus"
```

then this condition is true.

If another Python file imports `benchmark_runner.py`, then this condition is false.

This prevents the script from accidentally running when another file only wants to import something from it.

### Line 51

```python
    main()
```

This calls the `main` function.

Because it is inside the `if __name__ == "__main__":` block, it only runs when this file is executed directly from the command line.

## What this file does not do

This file does not:

- load prompt JSON by itself
- show prompts by itself
- ask for pasted answers by itself
- grade answers by itself
- save the detailed results by itself
- call an AI API

Instead, it launches another file, `manual_runner.py`, which handles the manual benchmark process.

## Mental model

Think of `benchmark_runner.py` as a remote control.

Right now, the only button on the remote is:

```text
manual
```

Pressing that button calls:

```python
run_manual_benchmark(...)
```

Later, the remote may have more buttons:

```text
manual
api
auto-grade
report
```

That is why this file exists even though it is currently small.
