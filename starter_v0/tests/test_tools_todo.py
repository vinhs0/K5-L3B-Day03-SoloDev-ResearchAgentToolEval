"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest  # noqa: F401

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](question="Chọn nguồn?", response_type="choice", options=["web", "twitter"])

    assert result["options"] == ["web", "twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "1", "section": "A"},
        {"title": "2", "section": "B"},
        {"title": "3", "section": "A"},
    ]
    md = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]

    assert md.count("## A") == 1
    assert md.count("## B") == 1
    assert md.index("- 1") < md.index("- 3") < md.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": "a"}, {"title": "b"}]
    md = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"]
    lines = [line for line in md.splitlines() if line]

    assert lines[0].startswith("1/")
    assert lines[1].startswith("2/")


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty, template="bullets")
        assert result["item_count"] == 0


def test_format_item_without_url_has_no_empty_link() -> None:
    md = TOOL_FUNCTIONS["format"](items=[{"title": "No link"}], template="bullets")["markdown"]

    assert "No link" in md
    assert "]()" not in md


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "tok123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "42"
    assert calls[0]["json"]["text"] == "Bản tin"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="x", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert result["items"] == []


def test_lookup_accepts_max_results_given_as_string(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="AI", max_results="7")

    assert calls[0]["json"]["max_results"] == 7


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://example.com/post"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/post",
        "source": "example.com", "summary": "# Hello",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    fake_http(FakeResponse({"data": {"markdown": "x" * 9000, "metadata": {}}}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com")

    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["title"] == "https://example.com"


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"screen_name": "sama", "text": "no id"}] + [
        {"screen_name": "sama", "tweet_id": str(i), "text": f"t{i}"} for i in range(1, 7)
    ]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    assert [i["url"] for i in result["items"]] == [f"https://x.com/sama/status/{n}" for n in (1, 2, 3)]


def test_timeline_without_key_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["timeline"](screenname="sama")
    assert result["error"] == "RuntimeError"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    calls = fake_http(FakeResponse({"timeline": []}))

    for search_type in ("Top", "Latest"):
        TOOL_FUNCTIONS["social_search"](query="GPT-5", search_type=search_type)

    assert calls[0]["params"] == {"query": "GPT-5", "search_type": "Top"}
    assert calls[1]["params"] == {"query": "GPT-5", "search_type": "Latest"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert TOOL_FUNCTIONS["policy"](query="")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = TOOL_FUNCTIONS["policy"](query="data privacy", policy_area="data_privacy")["results"]

    assert results
    assert {r["policy_area"] for r in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = TOOL_FUNCTIONS["policy"](query="injection probe", policy_area="source_citation")["results"]
    probe = [r for r in results if r["section"] == "Injection probe"]

    assert probe
    assert any("ignore the citation policy" in line for line in probe[0]["untrusted_text"])
    assert "ignore the citation policy" not in probe[0]["facts"]


# ---------------- wikipedia (new tool) ----------------

def test_wikipedia_maps_summary_and_builds_request(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Alan Turing", "extract": "British mathematician.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}},
    }))

    result = TOOL_FUNCTIONS["wikipedia"](title="Alan Turing", lang="en")

    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Alan_Turing"
    assert result["items"][0] == {
        "title": "Alan Turing", "url": "https://en.wikipedia.org/wiki/Alan_Turing",
        "source": "en.wikipedia.org", "summary": "British mathematician.",
    }


@pytest.mark.parametrize("kwargs", [{"title": ""}, {"title": "   "}, {"title": None}, {"title": "X", "lang": "xx"}])
def test_wikipedia_bad_input_returns_error_and_makes_no_request(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({}))

    result = TOOL_FUNCTIONS["wikipedia"](**kwargs)

    assert result["error"] == "ValueError"
    assert calls == []


def test_wikipedia_missing_page_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))
    assert TOOL_FUNCTIONS["wikipedia"](title="Nope")["error"] == "HTTPError"


# ---------------- hackernews (new tool) ----------------

def test_hackernews_sends_query_and_maps_hits(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "1", "title": "Show HN", "url": "https://a.dev", "points": 10, "num_comments": 2, "author": "bob", "created_at": "2026-01-01"},
        {"objectID": "2", "title": "Ask HN", "url": None, "points": None, "num_comments": None, "author": None},
        {"title": "no id is skipped"},
    ]}))

    result = TOOL_FUNCTIONS["hackernews"](query="LLM", sort="date", limit=3)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "LLM", "tags": "story", "hitsPerPage": 3}
    assert [i["title"] for i in result["items"]] == ["Show HN", "Ask HN"]
    assert result["items"][0]["summary"] == "10 points, 2 comments, by bob"
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=2"


def test_hackernews_bad_sort_or_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    assert TOOL_FUNCTIONS["hackernews"](query="")["error"] == "ValueError"
    assert TOOL_FUNCTIONS["hackernews"](query="x", sort="top")["error"] == "ValueError"
    assert calls == []


def test_hackernews_clamps_limit_and_tolerates_string_limit(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    TOOL_FUNCTIONS["hackernews"](query="x", limit=500)
    TOOL_FUNCTIONS["hackernews"](query="x", limit="7")
    TOOL_FUNCTIONS["hackernews"](query="x", limit="abc")

    assert [c["params"]["hitsPerPage"] for c in calls] == [20, 7, 5]


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))
    assert TOOL_FUNCTIONS["hackernews"](query="x")["error"] == "HTTPError"


# ---------------- current_time (new tool) ----------------

def test_current_time_returns_iso_date_and_weekday_for_utc() -> None:
    result = TOOL_FUNCTIONS["current_time"](timezone="UTC")

    assert result["timezone"] == "UTC"
    assert result["iso"].startswith(result["date"])
    assert result["iso"].endswith("+00:00")
    assert result["weekday"] in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}


def test_current_time_defaults_to_vietnam_timezone() -> None:
    for tz in ("", None):
        result = TOOL_FUNCTIONS["current_time"](timezone=tz)
        assert result["timezone"] == "Asia/Ho_Chi_Minh"
        assert result["iso"].endswith("+07:00")


def test_current_time_unknown_timezone_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["current_time"](timezone="Mars/Olympus")
    assert result["error"] == "ValueError"
