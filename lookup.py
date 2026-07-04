"""Lookup helpers for the india-pharma-hsn-gst dataset.

Pure stdlib, no dependencies. The dataset lives at data/hsn_gst.json
relative to this file.

    import lookup
    lookup.by_hsn("30049099")     # longest-prefix HSN match
    lookup.search("vaccine")      # free-text search
    lookup.gst_breakup(1000, 5)   # intra-state CGST/SGST split

Reference aid only — verify rates against current CBIC notifications
before using them for invoicing or GST return filing.
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "hsn_gst.json"

_cache = None


def load(path=None):
    """Load the dataset (list of entry dicts). Default path is cached."""
    global _cache
    if path is None:
        if _cache is None:
            with open(DATA_PATH, encoding="utf-8") as fh:
                _cache = json.load(fh)
        return _cache
    with open(Path(path), encoding="utf-8") as fh:
        return json.load(fh)


def _digits(code):
    """Normalize an HSN code to its digits only ('3004.90' -> '300490')."""
    return "".join(ch for ch in str(code) if ch.isdigit())


def by_hsn(code, entries=None):
    """Return the entry whose HSN is the LONGEST prefix of `code`.

    An 8-digit query like '30049099' resolves to the most specific entry
    available (a 6-digit '300490' beats the 4-digit '3004'). Returns
    None when no entry's HSN prefixes the query.
    """
    entries = load() if entries is None else entries
    code = _digits(code)
    if len(code) < 4:
        return None
    best, best_len = None, -1
    for entry in entries:
        hsn = _digits(entry.get("hsn", ""))
        if hsn and code.startswith(hsn) and len(hsn) > best_len:
            best, best_len = entry, len(hsn)
    return best


def search(term, entries=None):
    """Case-insensitive substring search over hsn/description/category/notes."""
    entries = load() if entries is None else entries
    needle = str(term).strip().lower()
    if not needle:
        return []
    results = []
    for entry in entries:
        haystack = " ".join(
            str(entry.get(key, ""))
            for key in ("hsn", "description", "category", "notes")
        ).lower()
        if needle in haystack:
            results.append(entry)
    return results


def gst_breakup(amount, rate):
    """Split an intra-state taxable amount into CGST + SGST halves.

    Returns {'taxable_value', 'gst_percent', 'cgst', 'sgst', 'total'}
    with money values rounded to 2 decimals.
    """
    amount, rate = float(amount), float(rate)
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if rate < 0:
        raise ValueError("rate must be non-negative")
    half = round(amount * rate / 200.0, 2)
    return {
        "taxable_value": round(amount, 2),
        "gst_percent": rate,
        "cgst": half,
        "sgst": half,
        "total": round(amount + 2 * half, 2),
    }
