# 06. Execute

[Previous](05-call.md) · [Next](07-history.md)

## What and why

Run the tool our code owns: HN search, one page of comments, or saving a digest. Return errors as data. Do not send the result back to the model yet.

## Check

```bash
pytest
```

`STEP` is 6, so later tests are skipped.

## Ready code

`src/news/api.py` calls the public HN Search API. `run_tool` validates input and performs the action. `execute_tool` catches failures and returns `{"error": ...}`.
