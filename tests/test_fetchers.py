"""
Tests for the source fetchers.

Network access is fully mocked with ``unittest.mock`` so the suite is fast,
deterministic and runnable offline / in CI (this is the "API testing" surface).
"""

from unittest.mock import MagicMock, patch

from fetchers.hackernews import fetch_hackernews
from fetchers.devto import fetch_devto


def _mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


# ── Hacker News ──────────────────────────────────────────────────────────────

@patch("fetchers.hackernews.requests.get")
def test_hackernews_filters_low_scores(mock_get):
    """Only stories with score > 100 should be returned."""
    top_ids = _mock_response([1, 2])
    high = _mock_response(
        {"title": "Big AI news", "url": "https://x.com/a", "score": 250}
    )
    low = _mock_response(
        {"title": "Minor note", "url": "https://x.com/b", "score": 12}
    )
    mock_get.side_effect = [top_ids, high, low]

    results = fetch_hackernews()

    assert len(results) == 1
    item = results[0]
    assert item["title"] == "Big AI news"
    assert item["source"] == "Hacker News"
    assert item["score"] == 250


@patch("fetchers.hackernews.requests.get")
def test_hackernews_falls_back_to_hn_permalink(mock_get):
    """Stories without a url should fall back to the HN item permalink."""
    top_ids = _mock_response([42])
    story = _mock_response({"title": "Ask HN", "score": 300})  # no 'url' key
    mock_get.side_effect = [top_ids, story]

    results = fetch_hackernews()

    assert results[0]["url"] == "https://news.ycombinator.com/item?id=42"


@patch("fetchers.hackernews.requests.get", side_effect=Exception("network down"))
def test_hackernews_returns_empty_on_failure(mock_get):
    """A network error must be swallowed and yield an empty list, not raise."""
    assert fetch_hackernews() == []


# ── Dev.to ───────────────────────────────────────────────────────────────────

@patch("fetchers.devto.requests.get")
def test_devto_maps_fields(mock_get):
    """Dev.to articles should be mapped to the common item schema."""
    article = {
        "title": "Cool Python trick",
        "url": "https://dev.to/x",
        "positive_reactions_count": 88,
        "description": "A neat description.",
    }
    mock_get.return_value = _mock_response([article])

    results = fetch_devto()

    assert len(results) > 0
    item = results[0]
    assert item["source"] == "Dev.to"
    assert item["score"] == 88
    assert item["summary"] == "A neat description."


@patch("fetchers.devto.requests.get", side_effect=Exception("boom"))
def test_devto_returns_empty_on_failure(mock_get):
    assert fetch_devto() == []
