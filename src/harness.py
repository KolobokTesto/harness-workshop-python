from dataclasses import dataclass, field

MAX_OUTPUT_TOKENS = 512
MODEL_TIMEOUT_SECONDS = 60

@dataclass
class Reply:
    stop_reason: str
    text: str
    tool_calls: list
    content: list
    request_body: dict | None = None

@dataclass
class ToolCall:
    tool_call_id: str
    tool_name: str
    input: object
    invalid: bool = False
    error: Exception | None = None

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
class Agent:
    model: object
    system: str
    tools: dict = field(default_factory=dict)
    run_tool: object = None
    context: str | None = None
    before_tool: object = None
    max_steps: int = 1

def run_agent(agent, task):
    messages = [{"role": "user", "content": task}]
    print(f"\nОдин запит. Повідомлень у запиті: {len(messages)}.")
    reply = agent.model.generate(system=agent.system, messages=messages, tools=list(agent.tools.values()), max_tokens=MAX_OUTPUT_TOKENS)
    if reply.stop_reason == "max_tokens":
        raise RuntimeError("Відповідь обрізано. Тули не виконуємо.")
    print("Модель відповіла. Це один запит без тулів.")
    return {"reason": "final", "text": reply.text, "messages": messages}
