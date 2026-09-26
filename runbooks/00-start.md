# 00. Setup

## What and why

Install Python 3.11 or newer, Git, and an editor. Create an Anthropic API key in the Claude Console. The workshop builds an agent that searches Hacker News and saves a digest. On the `start` branch the project layout, tests, and `.env.example` are ready. Practice changes `src/`.

## Check

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/check_setup.py
```

## Ready code

`src/main.py` prints `Python works.` Put `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL=claude-haiku-4-5` in `.env`.
