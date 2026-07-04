import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lookup  # noqa: E402


def test_load_returns_entries():
    entries = lookup.load()
    assert isinstance(entries, list)
    assert len(entries) >= 40
    for entry in entries:
        assert set(entry) == {"hsn", "description", "gst_percent", "category", "notes"}
        assert entry["hsn"].isdigit()
        assert entry["gst_percent"] in (0, 5, 12, 18)


def test_by_hsn_exact_match():
    entry = lookup.by_hsn("3004")
    assert entry is not None
    assert entry["hsn"] == "3004"
    assert entry["gst_percent"] == 5


def test_by_hsn_longest_prefix_wins():
    # 8-digit query should resolve to the 6-digit entry, not the 4-digit one
    entry = lookup.by_hsn("30049099")
    assert entry["hsn"] == "300490"
    assert entry["gst_percent"] == 5


def test_by_hsn_handles_formatting():
    assert lookup.by_hsn("3004.90")["hsn"] == "300490"


def test_by_hsn_unknown_returns_none():
    assert lookup.by_hsn("9999") is None
    assert lookup.by_hsn("") is None
    assert lookup.by_hsn("30") is None


def test_split_headings():
    assert lookup.by_hsn("300660")["gst_percent"] == 0  # contraceptives nil
    assert lookup.by_hsn("300610")["gst_percent"] == 12  # sutures
    assert lookup.by_hsn("902140")["gst_percent"] == 0  # hearing aids nil
    assert lookup.by_hsn("3306")["gst_percent"] == 18  # oral hygiene


def test_search_finds_vaccines():
    results = lookup.search("vaccine")
    assert results
    assert any(e["hsn"].startswith("3002") for e in results)


def test_search_empty_term():
    assert lookup.search("") == []
    assert lookup.search("   ") == []


def test_gst_breakup_splits_evenly():
    result = lookup.gst_breakup(1000, 5)
    assert result == {
        "taxable_value": 1000.0,
        "gst_percent": 5.0,
        "cgst": 25.0,
        "sgst": 25.0,
        "total": 1050.0,
    }


def test_gst_breakup_rounding():
    result = lookup.gst_breakup(99.99, 12)
    assert result["cgst"] == result["sgst"] == 6.0
    assert result["total"] == 111.99


def test_gst_breakup_rejects_negative():
    with pytest.raises(ValueError):
        lookup.gst_breakup(-1, 5)
    with pytest.raises(ValueError):
        lookup.gst_breakup(100, -5)
