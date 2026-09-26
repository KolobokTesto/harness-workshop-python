import os
import sys
import anthropic

MAX_OUTPUT_TOKENS = 512
MODEL = os.environ.get("ANTHROPIC_MODEL") or "claude-haiku-4-5"
task = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if not task:
    print("Помилка: передай задачу.", file=sys.stderr)
    raise SystemExit(1)
client = anthropic.Anthropic(max_retries=0)
reply = client.messages.create(
    model=MODEL,
    max_tokens=MAX_OUTPUT_TOKENS,
    timeout=60,
    system="Reply in Ukrainian.",
    messages=[{"role": "user", "content": task}],
)
text = "".join(block.text for block in reply.content if getattr(block, "type", None) == "text")
print("Причина завершення:", reply.stop_reason)
print("Відповідь:", text)
