import os
import anthropic

MAX_OUTPUT_TOKENS = 512
model_id = os.environ.get("ANTHROPIC_MODEL") or "claude-haiku-4-5"
client = anthropic.Anthropic(max_retries=0)
reply = client.messages.create(
    model=model_id,
    max_tokens=MAX_OUTPUT_TOKENS,
    timeout=60,
    messages=[{"role": "user", "content": "Привітайся українською одним реченням."}],
)
text = "".join(block.text for block in reply.content if block.type == "text")
print("Причина завершення:", reply.stop_reason)
print("Відповідь:", text)
