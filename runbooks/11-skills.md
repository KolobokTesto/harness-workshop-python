# 11. Skills

[Previous](10-context.md) · [Next](12-guard.md)

## What and why

The first message lists skill names and descriptions only. `readSkill` returns the full `SKILL.md` for a known name. Paths from the model are not opened.

## Check

The prompt contains the digest description and does not contain the skill body until after `readSkill`. `read_skill("../../.env")` raises `Невідомий skill`.

## Ready code

`src/skills.py` scans `skills/*/SKILL.md`. `skill_catalog()` is appended to context. The `readSkill` tool is registered next to the HN tools.
