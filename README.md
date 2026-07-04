# india-pharma-hsn-gst

A reference dataset + tiny stdlib lookup library for **Indian pharmaceutical HSN codes and GST rates**, derived from public CBIC (Central Board of Indirect Taxes and Customs) rate notifications.

If you build billing, ERP, or GST-filing software for Indian pharmacies, you need a machine-readable map from HSN chapter/heading to GST rate. This repo provides exactly that for the pharma-relevant chapters:

| Chapter / heading | Covers |
|---|---|
| 2936 | Provitamins and vitamins |
| 2937 | Hormones (incl. insulin) |
| 2941 | Antibiotics |
| 3001–3006 | Medicaments, vaccines, sera, dressings, sutures, diagnostic reagents |
| 3306 | Oral and dental hygiene preparations |
| 3401, 3402 | Soaps and washing preparations (common pharmacy counter items) |
| 9018–9022 | Medical, surgical, dental instruments and apparatus |
| 9402 | Medical, surgical, dental furniture |

## Dataset

`data/hsn_gst.json` is a flat JSON array. Each entry:

```json
{
  "hsn": "300490",
  "description": "Other medicaments, put up in measured doses or retail packs",
  "gst_percent": 5,
  "category": "medicaments",
  "notes": "Largest category for retail pharmacy items. 5% per the 56th GST Council decision (Sep 2025)."
}
```

- `hsn` — 4-, 6-, or 8-digit code (string, digits only).
- `gst_percent` — total GST rate (CGST + SGST, or IGST) as a number.
- `notes` — rate splits, exemptions, and caveats where a heading is not uniform.

## Provenance

Rates are compiled from public CBIC GST rate notifications (Notification No. 1/2017-Central Tax (Rate) and its amendments) and subsequent GST Council decisions, including the **56th GST Council meeting (September 2025)** rate rationalisation, under which medicaments (headings 3003/3004 and related pharma inputs such as vitamins and antibiotics) moved to **5%**, effective 22 September 2025.

Where a heading has rate splits (e.g., 3006 contraceptives are nil-rated while sutures attract GST), the split is captured either as a separate 6-digit entry or in `notes`.

## Usage

### Python (stdlib only, no dependencies)

```python
import lookup

# Longest-prefix HSN match: an 8-digit code resolves to the most
# specific entry available (6-digit beats 4-digit).
entry = lookup.by_hsn("30049099")
print(entry["description"], entry["gst_percent"])  # Other medicaments ... 5

# Free-text search over description / category / notes
for e in lookup.search("vaccine"):
    print(e["hsn"], e["gst_percent"])

# Intra-state CGST/SGST breakup for an invoice line
print(lookup.gst_breakup(1000, 5))
# {'taxable_value': 1000.0, 'gst_percent': 5.0, 'cgst': 25.0, 'sgst': 25.0, 'total': 1050.0}
```

### Plain JSON (any language)

```bash
# All 5% entries
jq '[.[] | select(.gst_percent == 5)]' data/hsn_gst.json

# Look up a heading
jq '.[] | select(.hsn == "3005")' data/hsn_gst.json
```

### Run the checks

```bash
python -m pytest tests/ -q
```

## Disclaimer

This dataset is a **reference aid only**, not tax advice. GST rates change via Council decisions and CBIC notifications; headings can have conditional splits, exemptions, and compensation-cess nuances that a flat table cannot fully capture. **Always verify against the current CBIC notifications (cbic-gst.gov.in) before using these rates for invoicing or return filing.** No warranty of accuracy or completeness is made.

## About

Maintained by the team behind [Nesayo](https://nesayo.com), an AI assistant for Indian pharmacies. A free interactive version of this lookup is available at [https://nesayo.com/tools/medicine-gst-calculator](https://nesayo.com/tools/medicine-gst-calculator).

Contact: hello@nesayo.com · Site: https://nesayo.com

## License

MIT — see [LICENSE](LICENSE). Contributions (corrections with a CBIC notification citation) are welcome via pull request.
