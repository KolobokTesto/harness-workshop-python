import os
from pathlib import Path

import anthropic

from src.harness import MAX_OUTPUT_TOKENS, MODEL_TIMEOUT_SECONDS, Reply, ToolCall

DEFAULT_MODEL = "claude-haiku-4-5"


class ClaudeModel:
    def __init__(self, model_id=None, client=None):
        self.model_id = model_id or os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL
        self.client = client or anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or "missing", max_retries=0)

    def generate(self, *, system, messages, tools, max_tokens):
        body = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "system": system,
            "messages": _wire_messages(messages),
        }
        if tools:
            body["tools"] = tools
        if os.environ.get("HARNESS_REQUESTS_PATH"):
            Path(os.environ["HARNESS_REQUESTS_PATH"]).open("a", encoding="utf-8").write(_dumps(body) + "\n")
        message = self.client.messages.create(**body, timeout=MODEL_TIMEOUT_SECONDS)
        return _reply(message, body)


def _dumps(body):
    import json
    return json.dumps(body)


def _wire_messages(messages):
    wired = []
    for message in messages:
        content = message["content"]
        if isinstance(content, list):
            blocks = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    blocks.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block["tool_use_id"],
                            "content": block["content"],
                        }
                    )
                else:
                    blocks.append(block)
            wired.append({"role": message["role"], "content": blocks})
        else:
            wired.append({"role": message["role"], "content": content})
    return wired


def _reply(message, body):
    content = []
    calls = []
    texts = []
    for block in message.content:
        kind = getattr(block, "type", None) or block.get("type")
        if kind == "text":
            text = getattr(block, "text", None) or block.get("text")
            texts.append(text)
            content.append({"type": "text", "text": text})
        elif kind == "tool_use":
            name = getattr(block, "name", None) or block.get("name")
            tool_id = getattr(block, "id", None) or block.get("id")
            tool_input = getattr(block, "input", None)
            if tool_input is None and isinstance(block, dict):
                tool_input = block.get("input")
            content.append({"type": "tool_use", "id": tool_id, "name": name, "input": tool_input})
            calls.append(ToolCall(tool_id, name, tool_input))
    return Reply(message.stop_reason, "".join(texts), calls, content, body)
