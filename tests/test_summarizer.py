"""Tests for the deduplication + summarization logic in processors.summarizer."""

import json
from unittest.mock import MagicMock, patch

from processors.summarizer import similar, deduplicate_items, process_and_summarize


def _item(title, score=0, url="http://x", source="Test", summary=""):
    return {
        "title": title,
        "score": score,
        "url": url,
        "source": source,
        "summary": summary,
    }


# ── similar() ────────────────────────────────────────────────────────────────

def test_similar_identical_strings():
    assert similar("OpenAI releases model", "OpenAI releases model") == 1.0


def test_similar_is_case_insensitive():
    assert similar("Hello World", "hello world") == 1.0


def test_similar_unrelated_strings_low():
    assert similar("Rust compiler update", "New coffee recipe") < 0.4


# ── deduplicate_items() ──────────────────────────────────────────────────────

def test_deduplicate_removes_near_duplicates():
    items = [
        _item("OpenAI launches GPT-5 model today", score=10),
        _item("OpenAI launches GPT-5 model today!", score=5),
    ]
    result = deduplicate_items(items)
    assert len(result) == 1


def test_deduplicate_keeps_higher_score():
    items = [
        _item("OpenAI launches GPT-5 model today", score=5),
        _item("OpenAI launches GPT-5 model today!", score=99),
    ]
    result = deduplicate_items(items)
    assert len(result) == 1
    assert result[0]["score"] == 99


def test_deduplicate_keeps_distinct_items():
    items = [
        _item("Rust 2.0 released with new borrow checker"),
        _item("Kubernetes adds native WASM support"),
        _item("PostgreSQL 18 ships async IO"),
    ]
    result = deduplicate_items(items)
    assert len(result) == 3


# ── process_and_summarize() ──────────────────────────────────────────────────

def test_process_empty_input_returns_placeholder():
    out = process_and_summarize([])
    assert out["top_20"] == []
    assert "No significant" in out["one_liner"]


@patch("processors.summarizer.ollama.Client")
def test_process_summarizes_and_ranks(mock_client_cls):
    """A mocked Ollama client should drive the summary; ranks re-assigned 1..N."""
    fake = MagicMock()
    fake.generate.return_value = {
        "response": json.dumps(
            {
                "top_20": [
                    {"rank": 1, "title": "A", "importance": 3, "url": "u"},
                    {"rank": 2, "title": "B", "importance": 9, "url": "u"},
                ],
                "one_liner": "Today in tech: mocked.",
            }
        )
    }
    mock_client_cls.return_value = fake

    out = process_and_summarize([_item("A"), _item("B")])

    # Sorted by importance desc, then ranks re-assigned starting at 1.
    assert out["top_20"][0]["title"] == "B"
    assert out["top_20"][0]["rank"] == 1
    assert out["top_20"][1]["rank"] == 2
    assert out["one_liner"] == "Today in tech: mocked."
