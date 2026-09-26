# 07. History

[Previous](06-execute.md) · [Next](08-loop.md)

## What and why

Append the assistant turn and each `tool_result` to `messages`, using the same tool-use id. The next request can see what happened.

## Check

A tool result message contains the original `tool_use_id`.

## Ready code

After execution, push `{role: assistant, content}` and a user message whose block type is `tool_result`.
