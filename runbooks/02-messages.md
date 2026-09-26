# 02. Messages

[Previous](01-model.md) · [Next](03-function.md)

## What and why

The task comes from the command line and is the user message. Standing rules go in `system`. An empty task exits before any HTTP call.

## Check

```bash
python -m src.main "Say hello in one Ukrainian sentence."
```

## Ready code

Read `sys.argv[1]`. If it is missing or blank, print `Помилка: передай задачу` and exit 1. Send `messages=[{"role": "user", "content": task}]` and `system="Reply in Ukrainian."`.
