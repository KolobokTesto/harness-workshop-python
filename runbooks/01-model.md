# 01. One request

[Previous](00-start.md) · [Next](02-messages.md)

## What and why

Send one Messages API request and print the reply. This checks that the Claude key and model work before any tools.

## Check

```bash
python -m src.main
```

## Ready code

`src/main.py` calls `client.messages.create` with model `claude-haiku-4-5`, `max_tokens` 512, and a short Ukrainian greeting prompt. `max_retries` is 0.
