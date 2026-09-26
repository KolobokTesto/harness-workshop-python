# Harness Workshop Python

Same workshop as the TypeScript harness: a small coding agent that searches Hacker News, reads comments, and saves a Ukrainian digest. The loop, tools, history, retries, project context, skills, and write guard are implemented in Python. The model is Claude through `ANTHROPIC_API_KEY`.

## Layout

- `src/main.py` reads the task from the command line.
- `src/harness.py` is the agent loop.
- `src/claude_model.py` calls the Anthropic Messages API.
- `src/news/` holds HN search and the tool definitions.
- `AGENTS.md`, `rules/`, and `skills/digest/SKILL.md` are the instructions the model sees.

## Setup

```bash
cd harness-workshop-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put your key in `.env`:

```
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-haiku-4-5
APPROVED=0
```

## Run

```bash
set -a && source .env && set +a
python -m src.main "Find one discussion about coding agents from the last 7 days. Read one page of comments and save a summary of up to 100 words with a link."
```

Writing `.data/digest.md` is blocked until you allow it:

```bash
APPROVED=1 python -m src.main "..."
```

Check the key:

```bash
python scripts/check_setup.py
```

## Tests

```bash
pytest
```

Tests use a fake model and mocked HN responses. They do not call Claude.

## Steps

`main` is the finished agent: one request, messages, `run_agent`, tool schemas, execution, history, the step loop, retries, project context, the digest skill, and the `APPROVED=1` guard.

`start` has no agent yet. Each later branch adds one step, in the same order as the TypeScript workshop. `main` matches `step-12-guard`. `STEP` is the checkpoint number, and `pytest` skips tests from later steps.
