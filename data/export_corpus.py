#!/usr/bin/env python3
"""
Export a CLEANED, honest free slice of the resolved-markets corpus for public
publish (HuggingFace / Kaggle). Read-only on the source (snapshots to /tmp).

Cleaning decisions (all honest, all documented in the dataset card):
  - DROP volume / volume24hr / liquidity — they are 100% zero (never captured);
    shipping all-zero columns would imply data that isn't there.
  - ADD resolved_date (ISO) derived from resolved_at for usability.
  - KEEP every distinct token_id row (each = one resolved binary outcome). Mark
    duplicate-question rows (multi-token markets) so users can dedupe if they want.
  - DO NOT attempt to "fix" category labels (they're noisy, e.g. NCAAB tagged
    'crypto'); leave as-is and flag in the card — silently re-labelling would be
    a worse lie than documenting the noise.
Output: CSV next to this script.
"""
import csv
import datetime as dt
import os
import shutil
import sqlite3

SRC = "./polyedge_history.db"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "polymarket_resolved_2022_2026.csv")


def main():
    snap = "/tmp/corpus_export.db"
    shutil.copy(SRC, snap)
    try:
        c = sqlite3.connect(snap).cursor()
        # count question multiplicity so we can flag dupes without dropping
        c.execute("CREATE INDEX IF NOT EXISTS _q ON resolutions(question)")
        rows = c.execute(
            "SELECT token_id, question, slug, resolved_yes, resolved_at, "
            "end_date, category FROM resolutions ORDER BY resolved_at"
        ).fetchall()
        qcount = {}
        for r in rows:
            qcount[r[1]] = qcount.get(r[1], 0) + 1
        n = 0
        with open(OUT, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["token_id", "question", "slug", "resolved_yes",
                        "resolved_at", "resolved_date", "end_date", "category",
                        "question_token_count"])
            for tok, q, slug, ry, rat, ed, cat in rows:
                iso = ""
                try:
                    if rat and rat > 0:
                        iso = dt.datetime.fromtimestamp(
                            rat, dt.timezone.utc).strftime("%Y-%m-%d")
                except Exception:
                    iso = ""
                w.writerow([tok, q, slug, ry, rat, iso, ed, cat, qcount.get(q, 1)])
                n += 1
        size_mb = os.path.getsize(OUT) / 1e6
        print(f"wrote {n} rows -> {OUT} ({size_mb:.1f} MB)")
        print(f"distinct questions: {len(qcount)}  "
              f"(multi-token markets flagged via question_token_count)")
    finally:
        try:
            os.remove(snap)
        except OSError:
            pass


if __name__ == "__main__":
    main()
