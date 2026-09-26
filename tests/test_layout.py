from pathlib import Path


def test_00_workshop_layout():
    root = Path(__file__).resolve().parent.parent
    example = (root / ".env.example").read_text(encoding="utf-8")
    assert "ANTHROPIC_API_KEY=" in example
    assert "claude-haiku-4-5" in example
    assert (root / "requirements.txt").exists()
    assert (root / "runbooks" / "00-start.md").exists()
    assert (root / "runbooks" / "12-guard.md").exists()
