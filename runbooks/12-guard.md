# 12. Guard

[Previous](11-skills.md)

## What and why

`saveDigest` writes `.data/digest.md` only when `APPROVED=1`. Any other value blocks the tool and returns `blocked, ask the user` to the model. Settings are not copied into the prompt.

## Check

```bash
pytest
APPROVED=1 python -m src.main "Find one coding-agents discussion from the last 7 days, read one page of comments, and save a 100-word summary with a link."
```

## Ready code

`src/settings.py` reads `APPROVED`. `before_tool` runs before `run_tool`. This branch matches `main`.
