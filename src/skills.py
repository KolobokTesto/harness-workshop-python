import os
import re
from pathlib import Path

from src.context import section

DIRECTORY = Path(__file__).resolve().parent.parent / "skills"


def _load():
    found = []
    if not DIRECTORY.is_dir():
        return found
    for name in sorted(os.listdir(DIRECTORY)):
        file = DIRECTORY / name / "SKILL.md"
        if not file.is_file():
            continue
        text = file.read_text(encoding="utf-8")
        match = re.search(r"^description: (.+)$", text, re.M)
        if not match:
            raise RuntimeError(f"Немає description у skill {name}")
        found.append({"name": name, "description": match.group(1), "text": text})
    return found


skills = _load()


def read_skill(name):
    skill = next((item for item in skills if item["name"] == name), None)
    if not skill:
        raise RuntimeError(f"Невідомий skill: {name}")
    return skill["text"]


def skill_catalog():
    header = "Before working on a task that matches one of these skills, call readSkill with its name."
    lines = [f"{skill['name']}: {skill['description']}" for skill in skills]
    return section("skills", "skills/", "\n".join([header, *lines]))
