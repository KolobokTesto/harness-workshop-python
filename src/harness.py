import json
import os
import time
from dataclasses import dataclass, field

MAX_OUTPUT_TOKENS = 512
MODEL_TIMEOUT_SECONDS = 60
DEFAULT_MAX_STEPS = 10
DEFAULT_MAX_RETRIES = 0


class ApiCallError(Exception):
    def __init__(self, message, status_code, headers=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_headers = headers or {}


class MaxRetriesExceeded(Exception):
    def __init__(self, errors):
        super().__init__("max retries exceeded")
        self.reason = "maxRetriesExceeded"
        self.errors = errors


@dataclass
class ToolCall:
    tool_call_id: str
    tool_name: str
    input: object
    invalid: bool = False
    error: Exception | None = None


@dataclass
class Reply:
    stop_reason: str
    text: str
    tool_calls: list
    content: list
    request_body: dict | None = None


@dataclass
class Agent:
    model: object
    system: str
    tools: dict = field(default_factory=dict)
    run_tool: object = None
    context: str | None = None
    before_tool: object = None
    max_steps: int = DEFAULT_MAX_STEPS


def first_message(agent, task):
    return {"role": "user", "content": task}


def run_agent(agent, task):
    messages = [first_message(agent, task)]
    limit = agent.max_steps or DEFAULT_MAX_STEPS
    for step in range(1, limit + 1):
        print(f"\nКрок {step}. Повідомлень у запиті: {len(messages)}.")
        reply = generate_with_retry(agent, messages)
        if os.environ.get("TRACE") == "1":
            print("HTTP-запит:", reply.request_body)
        if reply.stop_reason == "max_tokens":
            raise RuntimeError("Відповідь обрізано. Тули не виконуємо.")
        if not reply.tool_calls:
            print("Зупинка: модель відповіла без виклику тула.")
            return {"reason": "final", "text": reply.text, "messages": messages}
        messages.append({"role": "assistant", "content": reply.content})
        for call in reply.tool_calls:
            print(f"Модель просить {call.tool_name}:", call.input)
            result = execute_tool(agent, call)
            print(f"Результат {call.tool_name}:", result)
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": call.tool_call_id,
                            "tool_name": call.tool_name,
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    ],
                }
            )
        print(f"Додали результати. Повідомлень в історії: {len(messages)}.")
    print("Зупинка: досягли ліміту кроків. Задача може бути незавершена.")
    return {"reason": "limit", "text": "", "messages": messages}


def generate_with_retry(agent, messages):
    errors = []
    for attempt in range(DEFAULT_MAX_RETRIES + 1):
        try:
            return agent.model.generate(
                system=agent.system,
                messages=messages,
                tools=list(agent.tools.values()),
                max_tokens=MAX_OUTPUT_TOKENS,
            )
        except ApiCallError as error:
            errors.append(error)
            if attempt >= DEFAULT_MAX_RETRIES or not _retryable(error):
                if len(errors) > 1:
                    raise MaxRetriesExceeded(errors) from error
                raise
            delay_ms = _retry_delay_ms(error)
            time.sleep(delay_ms / 1000)
    raise MaxRetriesExceeded(errors)


def _retryable(error):
    return error.status_code in (429, 503)


def _retry_delay_ms(error):
    header = error.response_headers.get("retry-after")
    if header:
        return int(header) * 1000
    return 2000


def execute_tool(agent, call):
    try:
        if call.invalid:
            raise call.error
        blocked = agent.before_tool(call.tool_name) if agent.before_tool else None
        if blocked:
            raise RuntimeError(blocked)
        return agent.run_tool(call.tool_name, call.input)
    except Exception as error:
        if isinstance(error, Exception) and error.__class__ is not Exception:
            message = str(error)
        else:
            message = str(error)
        return {"error": message}
