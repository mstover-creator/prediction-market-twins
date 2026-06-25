# Polymarket Resolved Markets (2022–2026)

A cleaned, normalized slice of **resolved** binary prediction markets from [Polymarket](https://polymarket.com), with the realized YES/NO outcome for each market. Built from public Polymarket Gamma API metadata plus on-chain CTF resolutions. Intended for base-rate analysis, forecast calibration studies, and resolution-aware backtesting research.

> This dataset is **resolved-outcome metadata only**. It contains no order book, no price history, and no trade-level data (see Limitations). Its value is the *cleaned resolved-outcome slice and the YES base rate*, not proprietary or higher-fidelity market data.

## Summary

- **Rows:** 462,285 resolved binary markets (one row per outcome token)
- **Distinct questions:** 395,411 (some markets expose multiple outcome tokens, so question text repeats)
- **Resolution date range:** 2022-08-21 → 2028-01-01 (2,967 rows carry future-dated `resolved_at`/`end_date` values inherited from source metadata; treat far-future dates with caution)
- **Overall YES base rate:** **37.33%** of markets resolved YES
- **Format:** single SQLite table `resolutions` (trivially exportable to CSV/Parquet)
- **Source:** public Polymarket Gamma API + on-chain CTF (Conditional Token Framework) resolutions

## Schema

The data is one table, `resolutions`. `token_id` is the primary key.

| Column | Type | Meaning |
|---|---|---|
| `token_id` | TEXT (PK) | Polymarket CTF outcome-token identifier. Unique per row. |
| `question` | TEXT | The market question as posed on Polymarket (e.g. *"Will X happen by date Y?"*). Repeats across multi-token markets. |
| `slug` | TEXT | Polymarket URL slug for the market. |
| `resolved_yes` | INTEGER (0/1) | **The realized outcome for this token.** `1` = the market resolved YES (the YES side paid out / the condition occurred); `0` = it resolved NO. This is the label most users want. |
| `resolved_at` | INTEGER | Resolution timestamp, Unix epoch seconds (UTC). |
| `volume` | REAL | **Always 0 — not captured.** See Limitations. |
| `volume24hr` | REAL | **Always 0 — not captured.** See Limitations. |
| `liquidity` | REAL | **Always 0 — not captured.** See Limitations. |
| `end_date` | TEXT | Market end date as reported by source metadata (ISO-ish string). |
| `category` | TEXT | Source-provided category label (e.g. `politics_us`, `crypto`, `nba`, `other`). **Noisy** — see Limitations. |

### Outcome semantics (`resolved_yes`)

`resolved_yes` is the ground-truth binary outcome of the market as settled on-chain. A value of `1` means the YES condition was realized; `0` means it was not. Because the slice is restricted to *resolved* markets, every row has a definite outcome — there are no open or void markets in this table. Multi-outcome markets are represented as multiple binary token rows (one per outcome), so summing `resolved_yes` across the tokens of a single event will typically equal 1.

## Intended uses

- **Base rates.** Compute empirical resolution frequencies overall (37.33% YES) or sliced by question pattern / time period. Useful as priors for forecasting.
- **Calibration research.** If you pair these outcomes with your own price snapshots (this dataset does **not** include prices), you can study how well market-implied probabilities tracked realized outcomes.
- **Backtesting / event-study research.** A large, time-stamped corpus of binary events with known outcomes for resolution-aware analysis.
- **NLP on forecasting questions.** ~395k distinct natural-language questions with binary outcomes for text-classification or question-understanding work.

## Limitations

Please read these before using the data. They are material.

1. **`volume`, `volume24hr`, and `liquidity` are 100% zero.** These columns exist in the schema but were never populated during collection. Verified: 0 non-zero rows across all 462,285 rows. **Do not** use this dataset for any volume-, liquidity-, or trade-activity-based analysis. If you need trading data, this is the wrong dataset (see alternatives below).

2. **No prices, no order book, no time series.** This is resolved-outcome metadata only. There is no price history and no per-trade data. Calibration work requires you to supply your own price snapshots.

3. **`category` labels are noisy.** They come straight from source metadata and are frequently wrong. The largest bucket is `other` (162,202 rows). Concrete mislabels confirmed in the data: college/Olympic sports games tagged `crypto` (e.g. *"Fresno State vs. Nevada"*, *"Olympic Basketball: Canada vs. France"* both carry `category = 'crypto'`). Treat `category` as a weak, unreliable signal — derive your own labels from `question` text if categorization matters.

4. **Multi-token duplication.** 462,285 rows vs. 395,411 distinct questions: multi-outcome markets contribute several rows sharing the same `question`. Dedupe on `question` (or group by event) if you need one row per event rather than per outcome token.

5. **A few future-dated rows.** 2,967 rows have `resolved_at`/`end_date` in the future relative to collection, inherited from source metadata. Filter on `resolved_at <= now` if you want only definitively-settled history.

6. **Reproducible from public sources — not proprietary.** Everything here is derived from the public [Polymarket Gamma API](https://docs.polymarket.com) and on-chain CTF resolutions. Anyone can reconstruct it. The contribution is the cleaning, normalization, and the resolved-outcome + base-rate slice — not access to private data.

7. **Higher-fidelity free alternatives exist.** If you need trading data or richer fields, consider:
   - Kaggle Polymarket datasets (~100k markets, **with** trading/volume data),
   - the HuggingFace Polymarket dump (~107GB, much richer).

   Choose this dataset specifically when you want a large, clean, *resolved-outcome* base-rate slice and don't need volume/price.

## License & provenance

- **Provenance:** Public market metadata from the Polymarket Gamma API and publicly verifiable on-chain CTF resolution events. No private, gated, or scraped-behind-auth data.
- **License:** Released for research/educational use. The underlying facts (questions, outcomes, timestamps) are public market metadata; this packaging adds cleaning and normalization. Attribution appreciated. Verify Polymarket's terms before any commercial redistribution.
- This dataset is not affiliated with or endorsed by Polymarket.

## How to load

SQLite (the native format):

```python
import sqlite3, pandas as pd

con = sqlite3.connect("polymarket_resolved_2022_2026.db")
df = pd.read_sql_query("SELECT * FROM resolutions", con)

# Overall YES base rate
print(df["resolved_yes"].mean())          # ~0.3733

# One row per event (drop multi-token duplicates), settled only
import time
settled = df[df["resolved_at"] <= time.time()].drop_duplicates("question")
```

CSV export (if distributed as CSV):

```python
import pandas as pd
df = pd.read_csv("polymarket_resolved_2022_2026.csv")
```

> Reminder: `volume`, `volume24hr`, and `liquidity` are all zero — ignore those columns.