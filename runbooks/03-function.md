# 03. Function

[Previous](02-messages.md) · [Next](04-tools.md)

## What and why

Move the single request into `run_agent` so later steps can grow the loop without rewriting `main`.

## Check

```bash
pytest -m "step <= 3 or not step"
```

Run the tests introduced through this step. On this branch `STEP` is 3.

## Ready code

`src/harness.py` exports `Agent` and `run_agent`. It sends one request and returns `{reason, text, messages}`. `src/main.py` only parses the task and prints the result.
