import sys
from src.claude_model import ClaudeModel
from src.harness import Agent, run_agent

def main():
    task = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    if not task:
        print("Помилка: передай задачу.", file=sys.stderr)
        raise SystemExit(1)
    result = run_agent(Agent(model=ClaudeModel(), system="Reply in Ukrainian."), task)
    if result["text"]:
        print(f"\nВідповідь: {result['text']}")

if __name__ == "__main__":
    main()
