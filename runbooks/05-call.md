# 05. Call

[Previous](04-tools.md) · [Next](06-execute.md)

## What and why

Pass the tool list on the Claude request. Log each tool call. Stop after the model asks. Do not execute yet.

## Check

The first request includes a `searchStories` schema whose `query` property is a string.

## Ready code

`run_agent` calls `model.generate(..., tools=...)`. If `stop_reason` is `tool_use`, print each call and return.
