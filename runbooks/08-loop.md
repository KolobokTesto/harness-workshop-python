# 08. Loop

[Previous](07-history.md) · [Next](09-retry.md)

## What and why

Repeat the request until the model stops calling tools or `max_steps` is reached. Several tool calls in one turn each get their own result.

## Check

A search, then a read, then a save grows the message count. A model that keeps calling the same tool stops at the step limit. `max_tokens` does not execute tools.

## Ready code

`run_agent` loops `for step in range(1, max_steps + 1)`. No tool calls returns `reason=final`. Exhausting the loop returns `reason=limit`.
