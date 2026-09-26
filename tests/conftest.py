"""Skip tests that belong to a later workshop step. STEP is the checkpoint number."""

from pathlib import Path

import pytest

_STEP_FILE = Path(__file__).resolve().parent.parent / "STEP"


def pytest_configure(config):
    config.addinivalue_line("markers", "step(n): workshop checkpoint that introduces this test")


def pytest_collection_modifyitems(config, items):
    current = int(_STEP_FILE.read_text(encoding="utf-8").strip()) if _STEP_FILE.exists() else 12
    for item in items:
        mark = item.get_closest_marker("step")
        if mark and int(mark.args[0]) > current:
            item.add_marker(pytest.mark.skip(reason=f"introduced at step {mark.args[0]}"))
