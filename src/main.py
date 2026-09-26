import sys

from src.harness import Agent, run_agent
from src.news.agent import build_news


def main():
    task = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    if not task:
        print(
            'Помилка: передай задачу. Наприклад: python -m src.main "Знайди до трьох обговорень про harness engineering і coding agents за останні 7 днів. Прочитай коментарі та збережи український дайджест із посиланнями."',
            file=sys.stderr,
        )
        raise SystemExit(1)
    spec = build_news()
    agent = Agent(
        model=spec["model"],
        system=spec["system"],
        tools=spec["tools"],
        run_tool=spec["run_tool"],
        context=spec["context"],
        before_tool=spec["before_tool"],
    )
    try:
        result = run_agent(agent, task)
    except Exception as error:
        print("Помилка:", error, file=sys.stderr)
        raise SystemExit(1) from error
    if result["text"]:
        print(f"\nВідповідь: {result['text']}")
    if result["reason"] == "limit":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
