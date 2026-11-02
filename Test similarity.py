# CHANGED [Tests]: tijaabooyin otomaatig ah (pytest). Shaqaysii: python -m pytest -v
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import webcheck
from similarity import classify, cosine_score, jaccard_score, ngrams, shared_ngrams

TEXT_A = "Artificial intelligence is changing the world of education and helping students learn faster every day."
TEXT_B = "Volcanic eruptions release molten rock, ash and gases from deep beneath the surface of the planet."


def test_identical_documents_score_100():
    assert round(cosine_score(TEXT_A, TEXT_A) * 100, 1) == 100.0


def test_different_documents_score_near_zero():
    assert cosine_score(TEXT_A, TEXT_B) * 100 < 5


def test_classify_thresholds():
    assert classify(70) == "High Similarity"
    assert classify(40) == "Moderate Similarity"
    assert classify(39.9) == "Low Similarity"


def test_jaccard_identical_is_one():
    assert jaccard_score(TEXT_A, TEXT_A) == 1.0


def test_strip_refs_removes_citation_markers():
    assert "[1]" not in webcheck.strip_refs("Madeira[1] is an island[A].")


def test_shared_ngrams_finds_common_phrase():
    a = "the quick brown fox jumps over the lazy dog"
    b = "yesterday the quick brown fox jumps again"
    assert "the quick brown fox" in shared_ngrams(a, b, 4)
    assert len(ngrams(a.split(), 4)) == 6


def test_web_verdict_wording_has_no_plagiarized_label():
    for pct in (5, 20, 80):
        assert "lagiarized" not in webcheck.verdict(pct)
    assert webcheck.verdict(5).startswith("Low")
    assert webcheck.verdict(20).startswith("Moderate")
    assert webcheck.verdict(80).startswith("High")


def test_check_text_uses_database_documents(monkeypatch):
    monkeypatch.setattr(webcheck, "search_web", lambda q: [])
    docs = [("old.txt", "2026-01-01", TEXT_A)]
    assert webcheck.check_text(TEXT_A, docs)["pct"] > 90
    assert webcheck.check_text(TEXT_B, docs)["pct"] == 0
