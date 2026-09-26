# india-pharma-hsn-gst

Nesayo is billing, stock and compliance software for Indian retail pharmacies that runs in the browser on any phone or computer ([nesayo.com](https://nesayo.com/?utm_source=github&utm_medium=readme&utm_campaign=hsn_gst_dataset)). This repository is a reference dataset + tiny stdlib lookup library for **Indian pharmaceutical HSN codes and GST rates**, maintained by the team behind it and derived from public CBIC (Central Board of Indirect Taxes and Customs) rate notifications.

If you build billing, ERP, or GST-filing software for Indian pharmacies, you need a machine-readable map from HSN chapter/heading to GST rate. This repo provides exactly that for the pharma-relevant chapters:

| Chapter / heading | Covers |
|---|---|
| 2936, 2937, 2941 | Vitamins, hormones (incl. insulin), antibiotics (bulk) — several rows are product-dependent, see below |
| 3001–3006 | Medicaments, vaccines, sera, dressings, sutures, diagnostic reagents |
| 3306 | Oral and dental hygiene preparations |
| 3401, 3402 | Soaps and washing preparations (common pharmacy counter items) |
| 9018–9022 | Medical, surgical, dental instruments and apparatus |
| 9402 | Medical, surgical, dental furniture |

## Dataset

`data/hsn_gst.json` is a flat JSON array of 61 entries. Example (a fully-resolved row):

```json
{
  "hsn": "300490",
  "description": "Other medicaments, put up in measured doses or retail packs",
  "gst_percent": 5,
  "category": "medicaments",
  "notes": "",
  "source": "Notification No. 9/2025-Central Tax (Rate), dated 17 September 2025 (effective 22 September 2025), Schedule I, S. No. 234"
}
```

Some headings do not have one rate — the notification splits them by the specific product, not just the HSN code. Those rows carry `gst_percent: null`, and `notes` names the candidate rates and their serial numbers:

```json
{
  "hsn": "3306",
  "description": "Preparations for oral or dental hygiene (dentifrices, denture powders, mouthwash, dental floss)",
  "gst_percent": null,
  "category": "oral-hygiene",
  "notes": "Product-dependent: toothpaste (Sch I S. No. 246), tooth powder (HSN 3306 10 10, S. No. 247) and dental floss (HSN 3306 20 00, S. No. 248) are 5%. Other oral/dental hygiene preparations (mouthwash, denture fixative pastes/powders) are 18% under Schedule II S. No. 63. See the 6-digit entries below for a specific product.",
  "source": "Notification No. 9/2025-Central Tax (Rate), dated 17 September 2025 (effective 22 September 2025), Schedule I S. No. 246-248 vs Schedule II S. No. 63 — rate is product-dependent"
}
```

**9 of 61 rows carry `gst_percent: null`**: the Chapter 29 bulk-drug-intermediate family (2936/2937/2941 and their 6-digit children — Schedule II "all organic chemicals" at 18% vs Schedule I "drugs and medicines" at 5%, a classification call the source notification does not resolve for that chapter), 300290, 300620, 300630, 3306, 3401 and 9022. Never guess one of the candidate rates for these — read `notes` and classify per product.

Fields:
- `hsn` — 4-, 6-, or 8-digit code (string, digits only).
- `gst_percent` — total GST rate (CGST + SGST, or IGST) as a number, or `null` when the rate is product-dependent (see `notes`).
- `notes` — rate splits, exemptions, and caveats where a heading is not uniform.
- `source` — the notification, schedule and serial number this row's rate comes from.

## Provenance

Rates are compiled from two public CBIC Central Tax (Rate) notifications issued 17 September 2025, both effective 22 September 2025, giving effect to the 56th GST Council meeting:

- **Notification No. 9/2025-Central Tax (Rate)** (G.S.R. 641(E)) — the two-schedule rate structure (Schedule I = 5%, Schedule II = 18%) that superseded Notification 1/2017-CT(R). Neither Schedule I nor Schedule II of that notification sets a 12% rate for any of the goods in this dataset.
- **Notification No. 10/2025-Central Tax (Rate)** (G.S.R. 660(E)) — the nil-rate schedule that superseded Notification 2/2017-CT(R), including human blood and its components (S. No. 114), all types of contraceptives (S. No. 115) and hearing aids (S. No. 160).

Every row's `source` field cites the specific notification, schedule and serial number. Where a heading splits by product rather than by HSN code, `gst_percent` is `null` and `notes` names each candidate rate with its serial number — see "Dataset" above.

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

# Rows where the rate depends on the product (never guess these)
jq '[.[] | select(.gst_percent == null)]' data/hsn_gst.json

# Look up a heading
jq '.[] | select(.hsn == "3005")' data/hsn_gst.json
```

### Run the checks

```bash
python -m pytest tests/ -q
```

## CHANGELOG

See the repository's git commit history for exact dates. In order, oldest first:

- Initial release.
- Corrected 22 of 61 rows that carried the pre-reform rate structure (19 rows at a 12% slab, plus 330610/330620/340111 at 18% where Schedule I gives 5%). Added a `source` citation to every row. 9 product-dependent rows changed from a single asserted rate to `gst_percent: null` with candidate rates in `notes`, rather than asserting one of two possible values. Verified the two previously-unverified nil rows (300660, 902140) against the primary notification text. Replaced the README provenance paragraph, which cited an earlier, superseded notification.

## Disclaimer

This dataset is a **reference aid only**, not tax advice. GST rates change via Council decisions and CBIC notifications; several headings have conditional splits by product that a flat table cannot fully capture — those rows carry `gst_percent: null` rather than a guess. Some Chapter 30 "drugs and medicines" rows may also be affected by a separate list of specific fully-exempted drugs (Notification 10/2025-CT(R) Annexure I), which this dataset does not enumerate. **Always verify against the current CBIC notifications (cbic-gst.gov.in) before using these rates for invoicing or return filing.** No warranty of accuracy or completeness is made.

## About

Maintained by the team behind [Nesayo](https://nesayo.com/?utm_source=github&utm_medium=readme&utm_campaign=hsn_gst_dataset), billing, stock and compliance software for Indian retail pharmacies. A free medicine GST lookup tool is available at [nesayo.com/tools/medicine-gst-calculator](https://nesayo.com/tools/medicine-gst-calculator/?utm_source=github&utm_medium=readme&utm_campaign=hsn_gst_dataset) (it looks GST rates up from Nesayo's own medicine catalogue, a separate system from this repository).

Contact: hello@nesayo.com · Site: https://nesayo.com

## License

MIT — see [LICENSE](LICENSE). Contributions (corrections with a CBIC notification citation) are welcome via pull request.
