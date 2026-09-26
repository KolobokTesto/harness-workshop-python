import os
from pathlib import Path


def section(tag, source, text):
    return f'<{tag} source="{source}">\n{text.strip()}\n</{tag}>'


def load_context(root=None):
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    parts = [section("project", "AGENTS.md", agents)]
    rules = root / "rules"
    files = sorted(name for name in os.listdir(rules) if name.endswith(".md") and (rules / name).is_file())
    for name in files:
        text = (rules / name).read_text(encoding="utf-8")
        parts.append(section("rule", f"rules/{name}", text))
    return "\n\n".join(parts)
