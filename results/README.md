# Results

This folder stores benchmark results.

The first version of this project uses manual grading. A runner displays each prompt, the evaluator pastes a model answer, and then the evaluator records whether the model passed or failed.

## Planned Result Folders

```text
results/
  manual/
  api/
  reports/
```

## Manual Results

Manual results are created by `src/manual_runner.py`.

Each run saves a JSON file containing:

- the model name
- the dataset path
- the timestamp
- each prompt
- the pasted model answer
- pass/fail status
- optional numeric quality rating (0-100)
- severity if failed
- failure types if failed
- evaluator notes

## Future Results

Later versions may add:

- API-based runs
- automatic grading
- judge-model grading
- Markdown reports
- charts and summary statistics
