import json
import os
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest


def H():
    import src.harness as harness
    return harness


def N():
    import src.news.agent as news
    return news


class FakeModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def generate(self, *, system, messages, tools, max_tokens):
        self.calls.append({"system": system, "messages": messages, "tools": tools, "max_tokens": max_tokens})
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def text_reply(text="Готово."):
    return H().Reply("end_turn", text, [], [{"type": "text", "text": text}])


def call_reply(name, tool_input, tool_id="call_1"):
    call = H().ToolCall(tool_id, name, tool_input)
    return H().Reply(
        "tool_use",
        "",
        [call],
        [{"type": "tool_use", "id": tool_id, "name": name, "input": tool_input}],
    )


def agent_from(model, **overrides):
    spec = N().build_news(model)
    spec.update(overrides)
    return H().Agent(
        model=spec["model"],
        system=spec["system"],
        tools=spec["tools"],
        run_tool=spec.get("run_tool"),
        context=spec.get("context"),
        before_tool=spec.get("before_tool"),
        max_steps=spec.get("max_steps", 10),
    )


@pytest.mark.step(3)
def test_03_text_ends_after_one_request():
    model = FakeModel([text_reply()])
    result = H().run_agent(H().Agent(model=model, system="Reply in Ukrainian."), "Привіт")
    assert result["text"] == "Готово."
    assert result["reason"] == "final"
    assert len(model.calls) == 1
    assert model.calls[0]["messages"][-1]["role"] == "user"


@pytest.mark.step(5)
def test_05_model_receives_search_schema():
    model = FakeModel([call_reply("searchStories", {"query": "harness"}), text_reply()])
    H().run_agent(agent_from(model), "Перевір")
    tool = next(item for item in model.calls[0]["tools"] if item["name"] == "searchStories")
    assert tool["input_schema"]["properties"]["query"]["type"] == "string"


@pytest.mark.step(6)
def test_06_search_validates_arguments():
    with patch("src.news.api.urlopen", return_value=_json_response({"hits": []})):
        assert N().run_tool("searchStories", {"query": "harness"}) == []
    with pytest.raises(Exception):
        N().run_tool("searchStories", {"query": 42})
    for payload in ({"query": " "}, {"query": "agents", "days": 0}, {"query": "agents", "days": 31}):
        with pytest.raises(Exception):
            N().run_tool("searchStories", payload)


@pytest.mark.step(8)
def test_08_step_limit():
    model = FakeModel([call_reply("searchStories", {"query": "harness"})] * 2)
    result = H().run_agent(agent_from(model, max_steps=2), "Повторюй")
    assert result["reason"] == "limit"
    assert len(model.calls) == 2


@pytest.mark.step(8)
def test_08_unknown_tool_returns_error_to_model():
    model = FakeModel([call_reply("unknown", {}), text_reply()])
    H().run_agent(agent_from(model), "Некоректний виклик")
    blob = json.dumps(model.calls[1]["messages"], ensure_ascii=False)
    assert "error" in blob
    assert "Невідомий тул" in blob


@pytest.mark.step(8)
def test_08_truncated_output_does_not_run_tools():
    model = FakeModel([H().Reply("max_tokens", "", [H().ToolCall("c", "searchStories", {"query": "h"})], [])])
    executed = []

    def run(name, tool_input):
        executed.append(name)
        return {}

    with pytest.raises(RuntimeError, match="обрізано"):
        H().run_agent(agent_from(model, run_tool=run), "Перевір")
    assert executed == []


@pytest.mark.step(10)
def test_10_context_order():
    model = FakeModel([text_reply()])
    H().run_agent(agent_from(model), "Перевір джерела")
    user = model.calls[0]["messages"][0]["content"]
    project = user.index('<project source="AGENTS.md">')
    rule = user.index('<rule source="rules/sources.md">')
    task = user.index("<task>\nПеревір джерела\n</task>")
    assert project < rule < task
    assert "When comments disagree" in user
    assert "When comments disagree" not in model.calls[0]["system"]


@pytest.mark.step(11)
def test_11_skill_text_only_after_read():
    model = FakeModel([call_reply("readSkill", {"name": "digest"}), text_reply()])
    H().run_agent(agent_from(model), "Прочитай digest")
    first = json.dumps(model.calls[0]["messages"])
    second = json.dumps(model.calls[1]["messages"], ensure_ascii=False)
    assert "call readSkill" in first
    assert "Для пошуку спробуй" not in first
    assert "Для пошуку спробуй" in second
    with pytest.raises(RuntimeError, match="Невідомий skill"):
        from src.skills import read_skill
        read_skill("../../.env")


@pytest.mark.step(12)
def test_12_block_without_approval(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APPROVED", "0")
    model = FakeModel([call_reply("saveDigest", {"text": "Відповідь"}), text_reply()])
    H().run_agent(agent_from(model), "Надішли")
    assert not (tmp_path / ".data" / "digest.md").exists()
    assert "blocked, ask the user" in json.dumps(model.calls[1]["messages"])


@pytest.mark.step(12)
def test_12_approval_writes_digest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APPROVED", "1")
    model = FakeModel([call_reply("saveDigest", {"text": "Дозволено"}), text_reply()])
    result = H().run_agent(agent_from(model), "Надішли")
    assert result["reason"] == "final"
    assert (tmp_path / ".data" / "digest.md").read_text(encoding="utf-8").strip() == "Дозволено"


@pytest.mark.step(12)
def test_12_settings_not_in_prompt():
    model = FakeModel([text_reply()])
    H().run_agent(agent_from(model), "Перевір")
    blob = json.dumps(model.calls[0])
    assert "APPROVED" not in blob
    assert "permissions" not in blob
    previous = os.environ.get("APPROVED")
    os.environ["APPROVED"] = "0"
    try:
        assert N().before_tool("saveDigest") == "blocked, ask the user"
        os.environ["APPROVED"] = "1"
        assert N().before_tool("saveDigest") is None
    finally:
        if previous is None:
            os.environ.pop("APPROVED", None)
        else:
            os.environ["APPROVED"] = previous


@pytest.mark.step(9)
def test_09_retries_429_without_rerunning_tool(monkeypatch):
    waits = []
    monkeypatch.setattr("src.harness.time.sleep", lambda seconds: waits.append(int(seconds * 1000)))
    replies = [
        call_reply("searchStories", {"query": "harness"}, "save-1"),
        H().ApiCallError("limited", 429, {"retry-after": "21"}),
        text_reply(),
    ]
    model = FakeModel(replies)
    executions = []

    def run(name, tool_input):
        executions.append(name)
        return [{"id": 101}]

    H().run_agent(agent_from(model, run_tool=run, max_steps=2), "Збережи")
    assert executions == ["searchStories"]
    assert waits == [21000]


@pytest.mark.step(9)
def test_09_does_not_retry_401():
    model = FakeModel([H().ApiCallError("no", 401)])
    with pytest.raises(H().ApiCallError):
        H().run_agent(agent_from(model, max_steps=1), "Перевір")
    assert len(model.calls) == 1


@pytest.mark.step(9)
def test_09_max_retries(monkeypatch):
    monkeypatch.setattr("src.harness.time.sleep", lambda seconds: None)
    model = FakeModel([H().ApiCallError("limited", 429, {"retry-after": "1"})] * 3)
    with pytest.raises(H().MaxRetriesExceeded) as caught:
        H().run_agent(agent_from(model, max_steps=1), "Перевір")
    assert caught.value.reason == "maxRetriesExceeded"
    assert len(caught.value.errors) == 3


@pytest.mark.step(6)
def test_tool_descriptions():
    assert "up to 10 HN discussions" in N().TOOLS["searchStories"]["description"]
    assert "up to 10 comments" in N().TOOLS["readDiscussion"]["description"]
    assert "execute" not in N().TOOLS["searchStories"]


def _json_response(payload, status=200):
    body = json.dumps(payload).encode()

    class Resp:
        def __init__(self):
            self.status = status

        def read(self):
            return body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    return Resp()


@pytest.mark.step(6)
def test_06_hn_search_query(monkeypatch):
    seen = {}

    def fake_open(request, timeout):
        seen["url"] = request.full_url
        return _json_response({"hits": [{
            "objectID": "101", "title": "Harness", "url": "https://example.org",
            "points": 1, "num_comments": 2, "created_at": "2026-09-21T10:00:00Z",
        }]})

    monkeypatch.setattr("src.news.api.urlopen", fake_open)
    from src.news.api import search_stories
    stories = search_stories("tool calling", 3)
    assert "query=tool+calling" in seen["url"] or "query=tool%20calling" in seen["url"]
    assert stories[0]["url"] == "https://news.ycombinator.com/item?id=101"


@pytest.mark.step(6)
def test_06_hn_wrong_type(monkeypatch):
    monkeypatch.setattr("src.news.api.urlopen", lambda request, timeout: _json_response({"type": "comment"}))
    from src.news.api import read_discussion
    with pytest.raises(RuntimeError, match="id обговорення"):
        read_discussion(101)


@pytest.mark.step(6)
def test_06_http_error(monkeypatch):
    def boom(request, timeout):
        raise HTTPError(request.full_url, 429, "limited", hdrs=None, fp=None)
    monkeypatch.setattr("src.news.api.urlopen", boom)
    from src.news.api import read_discussion
    with pytest.raises(RuntimeError, match="HTTP 429"):
        read_discussion(101)
