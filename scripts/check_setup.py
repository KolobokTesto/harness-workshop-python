import os
import sys

import anthropic

from src.claude_model import DEFAULT_MODEL

MODEL = os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL


def main():
    key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        print("Встав ANTHROPIC_API_KEY у .env. Ключ не потрібно показувати в чаті.", file=sys.stderr)
        raise SystemExit(1)
    client = anthropic.Anthropic(api_key=key, max_retries=0)
    try:
        reply = client.messages.create(
            model=MODEL,
            max_tokens=128,
            timeout=60,
            tools=[{"name": "ready", "description": "Connection check; no external action.", "input_schema": {"type": "object", "properties": {}}}],
            tool_choice={"type": "tool", "name": "ready"},
            messages=[{"role": "user", "content": "Call ready with no arguments to verify the connection."}],
        )
    except anthropic.APIStatusError as error:
        hints = {
            401: "Перевір ANTHROPIC_API_KEY у .env та чи він не відкликаний.",
            403: "Перевір доступ до моделі в Claude Console.",
            404: "Звір ANTHROPIC_MODEL із доступними моделями.",
            429: "Досягнуто ліміт Anthropic. Зачекай перед повтором.",
        }
        print("Перевірка не пройшла:", hints.get(error.status_code, error.message), file=sys.stderr)
        retry_after = error.response.headers.get("retry-after")
        if retry_after:
            print(f"Retry-After: {retry_after}", file=sys.stderr)
        raise SystemExit(1) from error
    names = [block.name for block in reply.content if getattr(block, "type", None) == "tool_use"]
    if "ready" not in names:
        print("Запит пройшов, але коректного tool call немає.", file=sys.stderr)
        raise SystemExit(1)
    print(f"Готово: {MODEL}; ключ працює; tool call отримано.")
    print("Зроблено один запит до Claude. Можна починати етап 01.")


if __name__ == "__main__":
    main()
