# Adversarial Audit Procedure — how we falsified a phantom cross-venue "signal"

*Reproducibility + integrity note. Repo location: `analysis/AUDIT_PROCEDURE.md`.*

## Why this document exists

The methodology's central claim is that it is built **not to fool itself**. Pre-registration (sha256-frozen
criteria) guards against moving the goalposts after the fact. This adversarial audit guards against the
*opposite* failure — believing an exciting but buggy **positive**. When our own pipeline produced a large,
stable cross-venue "divergence," we did not trust it; we ran the audit below, which proved it was an
artifact. This document specifies that audit precisely enough to re-run, so the claim "we adversarially
tested our own positives" is verifiable rather than asserted.

> Honesty note: the deterministic part of this audit (the measurement scripts) is bit-reproducible. The
> adversarial part is a **multi-agent LLM workflow** — its exact outputs are not bit-reproducible, but the
> roles, prompts, verdict schema, and decision rule are fully specified here so anyone can re-run the
> *procedure* with any multi-agent setup.

## 1. The trigger — a 14°F "edge" that smelled wrong

The first scalar-twin measurement reported an implied-median gap of roughly **14°F** (≈ a 98-point
probability divergence) on a **Chicago daily-high temperature** twin between Polymarket-US and Kalshi. A gap
that large on a liquid, tightly-defined daily weather market is implausible on its face, and it resembled
the convention/freshness artifacts that had fooled earlier versions of the pipeline. Per the methodology, a
surprising positive is **presumed an artifact until adversarially cleared.**

## 2. The design

Multi-agent, adversarial, and blind. As run, the audit used **four agents**: independent re-derivation
agents plus a dedicated skeptic. *(If you saved the workflow run, attach its log / agent IDs here.)*

- **Independent re-derivation agents (run blind to one another).** Each receives only the raw per-venue
  quotes for the candidate twin — the Polymarket-US ladder/band prices and the Kalshi tail prices — plus the
  pipeline's reported gap. Task: independently reconstruct each venue's implied distribution from the raw
  quotes and compute the implied-median gap *by hand*, and state whether the reported signal reproduces.
- **Dedicated skeptic / red-team agent.** Explicitly tasked to **prove the signal is a measurement artifact**
  and to name the mechanism. Adversarial prior: default to "artifact" unless the signal survives every check.

Each agent returns a structured verdict:

```json
{ "signal_is_real": false,
  "implied_median_gap": "<value+unit>",
  "artifacts_identified": ["..."],
  "strongest_disqualifier": "...",
  "reasoning": "..." }
```

**Decision rule (deliberately conservative):** the signal is accepted only if the independent re-derivations
agree it reproduces **and** the skeptic fails to find a credible disqualifying artifact. Any one credible
named artifact rejects the signal. This makes a positive *hard to keep* — which is the point.

## 3. The verdict

All four agents converged on **`signal_is_real = false`**. The skeptic and the re-derivations jointly
identified the cause — principally **series contamination**: keying twins on `(city, date)` had merged three
*different* Kalshi series that share a city and date —

- `KXHIGH` (daily **high**),
- `KXLOWT` (daily **low**),
- `KXTEMP` (an **instantaneous** ~2pm reading) —

into a single "temperature for Chicago on date D" curve. Collapsing a high, a low, and a spot reading into
one distribution dragged the implied median by ~14°F and fabricated the ~98-point gap against Polymarket's
daily-high market. The audit also surfaced the rest of the catalog (the ≥/> convention, bands-vs-tails,
subject-collapse, and sign-drop + ~26% overround) as contributing or analogous artifacts.

## 4. The corrected re-measurement

After fixing the named artifacts — **split the matching key on the series/metric**, normalize the ≥/>
convention, reconstruct each venue's implied distribution, and compare the **implied median** (robust to a
uniform overround and to per-bin noise) rather than strike labels — an end-to-end re-measurement reproduced
**agreement to ~0.1°F** across the twin universe (weather implied-median gaps ≤ 0.11°F; macro within
hundredths of a point). The phantom edge was entirely a measurement artifact, exactly as the audit predicted.

## 5. How to reproduce

### Deterministic part — scripts (`analysis/`)
- `scalar_twin_measure.py` — the scalar-twin measurement: distribution reconstruction, ≥/> convention
  handling, series-split keys, and the §3 artifact-catalog gates.
- `remeasure_scalar_twins.py` — the corrected end-to-end re-measurement that produced the agreement table.
- `macro_twin_probe.py`, `xvenue_catalog_join_diag.py`, `explore_scalar_twins.py`, `analyze_macro_dump.py` —
  diagnostics that isolate each artifact class.

These are deterministic given the same input snapshots.

### Adversarial part — LLM workflow (prompt templates)

**Re-derivation agent (run ≥2, blind to each other):**
> You are given the raw quoted prices for the twin **[metric, subject, reference period]** on two venues:
> Venue A = **[ladder/band quotes]**, Venue B = **[tail quotes]**. Independently reconstruct each venue's
> implied probability distribution over **[underlying quantity]** and compute the implied-median gap. Do
> **not** assume the previously reported gap is correct. Return the verdict JSON above.

**Skeptic / red-team agent:**
> A pipeline reports a **[X]-unit** cross-venue divergence on the twin **[…]**. Your job is to **prove this
> is a measurement artifact**, not a real disagreement. Check at minimum: (a) ≥ vs > threshold convention;
> (b) band-vs-tail object mismatch; (c) whether the two venues' series are actually the **same metric**
> (e.g., daily-high vs daily-low vs instantaneous — inspect the series tickers); (d) subject/transformation
> collapse (country, YoY vs QoQ); (e) sign-parsing and overround. **Default to "artifact" unless the signal
> survives every check.** Return the verdict JSON above, including `strongest_disqualifier`.

**Apply the decision rule** from §2 to the collected verdicts.

## 6. The lesson

Pre-registration stops you from *inventing* a positive after the fact. This audit stops you from *believing*
one you produced by accident — the harder of the two, because the buggy positive is the exciting one.
Running an adversarial audit on your own surprising results, by default, is the cheap habit that separates a
real negative result from a press release.
