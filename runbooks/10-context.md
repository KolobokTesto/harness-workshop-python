# 10. Context

[Previous](09-retry.md) · [Next](11-skills.md)

## What and why

Load `AGENTS.md` and every `rules/*.md` into the first user message, each wrapped in a tagged block. The task is last. `system` stays the agent role, not the project files.

## Check

The first user message contains `<project source="AGENTS.md">`, then `<rule source="rules/sources.md">`, then `<task>`.

## Ready code

`src/context.py` reads those files in sorted order. `first_message` joins context and `<task>`.
