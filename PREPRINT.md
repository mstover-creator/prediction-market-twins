# Comparing Prices Across Prediction-Market Venues Is Mostly a Measurement Problem: A Methodology and an Artifact Catalog

*A solo independent research note*

> **Pre-submission note (updated 2026-06-24):** Section 6 (Related Work) now cites real,
> dated papers — see the References section. **One verification to-do remains:** the
> Ng/Peng/Tao/Zhou SSRN entry (No. 5331995) was sourced via search and its SSRN page could
> not be fetched directly — confirm the abstract ID, exact title, author order, and year on
> SSRN before submitting. The other three (arXiv:2603.03136, arXiv:2508.03474 / AFT 2025,
> arXiv:2605.00864) were verified from their arXiv abstract pages. Separately, the
> `[REPO_URL]` / `[DATASET_URL]` / `[POSTMORTEM_URL]` fields in §8 still need the live URLs
> once the repo / dataset / postmortem are published.

## Abstract

Cross-venue price divergence — Polymarket and Kalshi quoting different probabilities for "the same event" at the same moment — is an appealing target: it is the one signal a single-venue observer structurally cannot reproduce, and a persistent, fee-clearing gap would be both a tradeable edge and a publishable dataset. I report that, wherever two major prediction-market venues genuinely list the same resolvable proposition in volume, their prices agree to within noise, and wherever they might disagree, they do not list the same proposition. This null is *not* the contribution: there is already a substantial 2024–2026 literature on Polymarket/Kalshi price-discovery and efficiency. The contribution is the **measurement methodology** required to reach that null without manufacturing false positives, and a **taxonomy of cross-venue measurement artifacts** — each of which fabricated a spurious "edge" (a phantom 14°F weather divergence, a ~12-point macro divergence) that a naïve pipeline would have published. I describe a pre-registered, fee-netted, freshness-filtered instrument with a three-stage twin-mapping procedure; an apples-to-apples extension to Polymarket's CFTC-regulated US venue (same jurisdiction as Kalshi); the five artifact classes and how each is corrected; and the single methodological fix — compare reconstructed implied *distributions* (median / survival function) for a (metric, subject, reference-period) twin, not raw strike labels. Results across daily city temperature and monthly U.S. macro prints show implied-median gaps of ≤0.11°F and ≤0.06pp once the method is applied.

## 1. Introduction

Prediction markets aggregate dispersed beliefs into a price, and the question of whether that price is informationally efficient has an established empirical literature. A natural sharpening of the efficiency question is *cross-venue*: do two independent markets, with different user bases, fee schedules, jurisdictions, and resolution sources, agree on the probability of the same future event? If they systematically disagree by more than transaction costs, that is simultaneously an arbitrage and evidence against joint efficiency. If they agree, that is a strong, replicated efficiency result obtained from genuinely independent order flow.

The appeal of cross-venue divergence to a practitioner is specific: a single-venue scraper, however good, cannot produce it. It is the one feature of the data that requires simultaneous, time-aligned observation of two independent books. I set out to measure it honestly — to determine whether Polymarket and Kalshi disagree on shared events in a way that survives fees, spreads, and stale quotes.

The hard problem turns out not to be the price. It is **same-event identity**. "The same topic" is everywhere — both venues carry weather, macroeconomic releases, elections, sports. "The same resolvable proposition" — identical metric, identical subject, identical reference period, identical resolution convention — is rare, and is precisely where any opportunity would have to live. Worse, the gap between "same topic" and "same proposition" is where measurement error hides: a pipeline that matches on topic and compares strike labels will report large, confident divergences that are entirely artifacts of mismatched conventions. The bulk of the engineering effort, and the bulk of this note, is about not being fooled by those artifacts.

I am a single operator working with roughly $406 of capital and one small VPS; this constrains the instrument (LLM calls are budgeted) and the scale (snapshot mids, not a continuous tape). I flag these limits throughout. The methodology is intended to be portable to a larger effort; the null is reported as a replication of existing results, not as a discovery.

## 2. The instrument

The instrument was built with the same discipline that produced an earlier clean negative on a different thesis (an LLM-directional signal test, pre-registered, that returned signal-dead at n=540, p=2.3×10⁻⁴⁹). The point of that discipline is to make a positive result *hard* to produce by accident.

**Pre-registration, sha256-frozen.** Before collecting evaluation data, I wrote down the success criteria, the era/configuration tag, and the scoring rules, and hashed the file. The hash is recorded with the results. You cannot move a goalpost you have already published the hash of. This is cheap and it is the single most valuable habit for self-funded work, where the temptation to retrofit a positive is strongest.

**Three-stage twin mapping.** Deciding that a Polymarket market and a Kalshi market are "the same event" is where wishful matching enters. I gate it in three stages, cheapest and most conservative first:

1. *Structural date gate.* If the two markets' resolution windows cannot overlap, they cannot be twins. This is a pure structural filter, applied before any expensive recognition.
2. *Budgeted LLM recognition.* Survivors are passed to a language model asked a narrow question: does this Polymarket market describe the same real-world resolvable event as this Kalshi market? It is budgeted deliberately — calls cost money — so the date gate must prune aggressively first.
3. *Price-geometry polarity veto.* Even an LLM-confirmed pair is rejected if its price geometry is inconsistent with being the same proposition: genuine twins must move with consistent polarity. If the geometry disagrees with the semantic match, the geometry wins. This catches the cases where the model recognizes a shared *topic* but the two markets resolve on different *propositions*.

**Fee-netting and spread verification.** A gap is counted as economically real only after netting taker fees and measuring against actual bid/ask, never midpoints. This matters because Polymarket's 2026 dynamic taker fee can consume the great majority of a nominal gap; a divergence that looks tradeable on mids can be entirely inside the round-trip cost.

**Freshness / both-legs-active filter.** This is the filter I most want a future builder to copy, and to build *first* rather than last. Many apparent divergences were liquidity artifacts: one venue's quote frozen — in one observed case stale by roughly 30 hours — so the "disagreement" was one leg failing to update, not two markets disagreeing. The filter requires both legs to be active and recently updated before a gap is admitted.

**The apples-to-apples extension (Polymarket-US / QCEX).** An obvious objection to any null found on Polymarket-International is jurisdictional: perhaps the international venue and Kalshi simply attract different flow. Polymarket's US, CFTC-regulated venue (QCEX) — the *same* regulatory jurisdiction as Kalshi — removes that confound. I rebuilt the instrument against it (Ed25519-signed REST/WebSocket, per-outcome slug handling) so that the comparison is between two CFTC-regulated venues. The result splits cleanly by market type, reported in §5.

## 3. A taxonomy of cross-venue measurement artifacts

This section is the core contribution. Each artifact below independently manufactured a phantom edge in an early version of the pipeline — a "divergence" large and stable enough that a naïve analyst would have published or traded it. All five are conjunctions of innocuous-looking choices; none is exotic. They are presented in the order in which they bit.

**3.1 Inclusive-vs-strict threshold convention (≥ vs >).** Polymarket states scalar thresholds inclusively — "≥ X" ("gte"/"atl" in the metadata); Kalshi states them strictly — "> X" ("above"). For a quantity reported to one decimal place, Kalshi's "> 4.3%" is the *same event* as Polymarket's "≥ 4.4%". A pipeline that aligns on the printed number compares "≥ 4.4%" against "> 4.4%", which differ by exactly one reporting tick. *Worked example:* across every monthly macro print (unemployment, GDP, payrolls, CPI), this one-tick misalignment fabricated a roughly **12-point** divergence — stable, repeatable, present in every release, and therefore exactly the kind of signal one is tempted to believe. Aligning the convention collapses the gap to roughly 2 points, within spread.

**3.2 Bands vs tails.** Polymarket weather markets are *bands* ("72–73°F"); Kalshi weather markets are *tails* ("above 72°F"). A band and a tail are different objects: P(72 ≤ T ≤ 73) is not P(T > 72). Comparing the raw strike labels — both of which mention 72 — compares incommensurable quantities. There is no convention fix here; the only correct move is to reconstruct each venue's full implied distribution and compare a common functional (see §4).

**3.3 Series contamination.** Keying twins on (city, date) for weather merged three *different* Kalshi metrics that share a city and date: daily-high (`KXHIGH`), daily-low (`KXLOWT`), and 2pm-instantaneous temperature (`KXTEMP`). Collapsing daily-high, daily-low, and an instantaneous reading into one "temperature for Chicago on date D" curve dragged the implied median by roughly **14°F** and produced a fake ~98-point probability gap against the Polymarket daily-high market. The metric is encoded in the series ticker; the matching key must split on it. This was the artifact that most resembled a real, exciting signal, and it is what triggered the adversarial audit described in §4.

**3.4 Subject collapse.** Defaulting every macro market's subject to "US" merged United States, Italian, German, and French GDP — and year-over-year with quarter-over-quarter — into a single comparison bucket. The resulting "divergence" is garbage by construction: it is comparing the U.S. economy to a weighted mash of European ones. Subject (country) and transformation (YoY vs QoQ) must be parsed into the matching key, not defaulted.

**3.5 Sign-dropping and overround.** Two compounding numerical hazards. First, a strike-parsing regex that dropped a leading minus folded negative GDP strikes onto their positive mirror images, corrupting the low tail of the distribution. Second, Polymarket scalar *ladders* are substantially overround: in the observed data the per-bin implied probabilities summed to roughly 1.26 (a ~26% overround, consistent with thinly-traded or model-priced ladders), so individual bin probabilities are not trustworthy point estimates. The implied **median** — the *location* of the distribution — is robust to a modest overround and to noise in individual bins in a way that any single bin's probability is not, which motivates the method in §4.

The unifying lesson: every one of these artifacts is produced by comparing **strike labels** across venues. None survives comparing distributions.

## 4. The correct method

The fix is a single change of comparison object:

> **Do not compare strike labels. For each (metric, subject, reference-period) twin, reconstruct each venue's implied probability distribution over the underlying quantity, and compare the venues on a common functional of that distribution — the implied median, and the survival function at shared points.**

Concretely: for a given metric/subject/period, take each venue's ladder or band/tail structure, convert quoted prices to implied probabilities, assemble them into a (possibly coarse) implied CDF over the underlying real-valued quantity, and read off the median. The median is chosen deliberately: it is the location of the distribution, it is insensitive to a uniform overround, and it is robust to noise in any individual bin. Where finer comparison is wanted, the survival function S(x) = P(Q > x) can be compared at strikes both venues quote, after the ≥/> convention is normalized so that "x" means the same thing on both sides.

This is the change that turns the phantom 14°F / 98-point series-contamination "signal" into the true agreement of roughly 0.1°F once the contaminating series are split out and the distributions are reconstructed per metric.

**Adversarial verification.** Because the first scalar measurement reported a 14°F weather "edge" — and because it smelled exactly like the convention and freshness artifacts that had fooled me before — I did not trust my own positive. I ran the suspicious result through a multi-agent adversarial audit: several independent agents each re-derived a candidate twin by hand from the raw data, and a dedicated skeptic agent was tasked with proving the result was an artifact. All converged on *signal-is-real = false* and named the bugs in §3. A corrected, end-to-end re-measurement then reproduced agreement to roughly 0.1°F across the twin universe. I emphasize this because the same discipline that produces a clean negative must also be willing to kill a buggy positive; the second is harder.

## 5. Results

**Where twins do and do not exist (PM-US vs Kalshi, both CFTC-regulated).**

- *Politics:* 82 LLM mapping attempts, **0 confirms**. Polymarket-US is granular (per-candidate primaries, per-district, "midterm winner"); Kalshi lists party-wins-the-general at a different horizon. Same proper nouns, different resolvable question.
- *Sports:* **0 of 15** candidate pairs even survive to a confirm. The venues list *different kinds* of sports markets — season futures and method-of-victory props on one side, novelty and championship futures on the other — not the same dated games.
- *Scalar ladders:* this is where twins genuinely exist in volume. A targeted fetch found 4,251 Kalshi scalar markets against Polymarket-US daily-weather and macro ladders. Here there are many true twins — and here, once parsed correctly, the venues agree.

**Implied-median gaps on confirmed scalar twins** (after convention alignment, series split, and distribution reconstruction):

| Twin (metric, subject, period) | Implied-median gap |
|---|---|
| Daily high temperature, Chicago | 0.01 °F |
| Daily high temperature, Miami | 0.05 °F |
| Daily high temperature, NYC | 0.07 °F |
| Daily high temperature, Los Angeles | 0.11 °F |
| GDP, United States, Q2 | 0.06 pp |
| Unemployment, United States, June | ~0.001 pp (convention-adjusted) |

For context, Kalshi bid/ask spreads on these markets ran 1.5–6 points. The agreement is therefore not an artifact of frozen books: these are liquid markets with real spreads that nonetheless agree to a small fraction of a degree, or a few hundredths of a percentage point, on the location of the implied distribution. The gaps are an order of magnitude or more inside the spread, let alone inside the round-trip fee.

The combined picture across §5 is the null stated in the abstract: where the two venues co-list the same proposition in volume (scalar ladders) they agree to within noise; where they might disagree (politics, sports) they do not co-list the same proposition. There is no observed regime providing both real twins and a persistent beyond-spread gap.

## 6. Related work

I want to be precise about what is and is not novel here. The efficiency of prediction markets, and specifically cross-platform price discovery between Polymarket and Kalshi, is an active and crowded area of 2024–2026 research. Ng, Peng, Tao, and Zhou (2026) study price discovery across Polymarket, Kalshi, PredictIt, and Robinhood on common contracts around the 2024 U.S. presidential election and find that Polymarket tends to *lead* Kalshi when liquidity and trading activity are high, alongside economically meaningful — and, on our reading, largely transient — cross-platform price disparities. On single-venue efficiency, Tsang and Yang (2026) document Polymarket maturing over the 2024 cycle, with arbitrage-deviation half-lives falling from hours to under a minute and Kyle's λ dropping by more than an order of magnitude; Saguillo, Ghafouri, Kiffer, and Suarez-Tangil (2025, AFT) catalogue rebalancing and combinatorial arbitrage within and across Polymarket markets (estimating tens of millions of dollars extracted historically); and Cheng, Yang, and Zou (2026), reconstructing markets from roughly 75 million order-book snapshots, find NBA-market mispricings structurally bounded by liquidity and confined to retail scale. **The finding that the two venues agree where they genuinely co-list the same proposition — that cross-venue prices are efficient — is consistent with this literature and is not claimed as a contribution.** Where that literature reports cross-venue disparities, they are concentrated in high-volume political contracts; in the terms of §3 and §5 those venues share proper nouns but not the same resolvable proposition (differing horizons and granularities), which is precisely the identification problem this note's instrument is built to make explicit rather than assume away.

What I claim as contributions are narrower and, I believe, complementary:

1. The **cross-venue measurement methodology** — the three-stage twin mapping with a price-geometry polarity veto, fee-netting against real bid/ask, the both-legs-active freshness filter, and the pre-registration/hash discipline — assembled as a reusable instrument.
2. The **apples-to-apples Polymarket-US (QCEX) instrument**, which removes the jurisdictional confound by comparing two CFTC-regulated venues rather than an offshore venue against a regulated one.
3. The **artifact catalog** of §3: five concrete, reproducible ways that a topic-and-strike-label matching pipeline manufactures phantom cross-venue divergence, with worked magnitudes (≈12pt macro, ≈14°F / ≈98pt weather). I have not seen these failure modes catalogued together, and they are the practical obstacle between "two venues quote the same topic" and "two venues are measured to agree."

In short: the null is a replication; the *route to trusting the null* is the work.

## 7. Limitations

This is a small, self-funded study and its limits are material.

- **Snapshot mids, not a tape.** Measurements are point-in-time snapshots, not a continuous synchronized tape. Microstructure-timing effects (lead-lag at sub-snapshot resolution) are out of scope; I can speak to agreement in level, not to who moves first.
- **Polymarket overround.** Polymarket scalar ladders were ~26% overround in the observed data, which is why I rely on the implied median rather than per-bin probabilities. A study with cleaner per-bin pricing could compare full distributions more aggressively.
- **Single operator, budgeted LLM.** The LLM recognition stage is budget-constrained; a richer recognition budget might confirm more borderline twins, though the structural and geometry gates make false *positives* the controlled risk.
- **Scale.** Confirmed scalar twins number in the low thousands of candidate markets, not the hundreds of thousands seen in the large academic studies. The agreement I report is strong on the twins examined but is not a population-level efficiency estimate.
- **Resolution-source residual risk.** Even spec-identical twins can resolve on slightly different official data sources; convention alignment handles the stated threshold, not a divergence in the underlying print's source or vintage.

None of these weakens the methodological contribution, and none changes the direction of the result.

## 8. Reproducibility

Everything required to reproduce or extend the measurement is released:

- **The pre-registration discipline.** Success criteria, era tag, and scoring rules are committed and sha256-hashed before evaluation data is collected; the hash travels with the results, so the target is verifiable as having been fixed in advance.
- **The open-source instrument.** The cross-venue divergence watcher (structural date gate → budgeted LLM recognition → price-geometry polarity veto), the fee-netting and spread-verification, and the both-legs-active freshness filter.
- **The scalar-twin measurement scripts.** Distribution reconstruction, the ≥/> convention handling, the series-split keys, and the artifact-catalog gates of §3, plus the corrected end-to-end re-measurement that produced the agreement in §5. The multi-agent adversarial audit that initially falsified the weather "signal" is documented as a reproducible procedure (`AUDIT_PROCEDURE.md`) — the agent roles, prompt templates, verdict schema, and decision rule — rather than shipped as a deterministic binary, since the audit is an LLM workflow whose exact outputs are not bit-reproducible.
- **A companion corpus.** A cleaned, normalized slice of 462,285 resolved Polymarket binary markets (2022-08 → 2026; 37.33% YES base rate; ~395,411 distinct questions), derived entirely from the public Polymarket Gamma API and on-chain CTF resolutions. I offer it as a convenience and citation resource only, with explicit caveats: its `volume`/`volume24hr`/`liquidity` columns are 100% zero (never captured), its `category` labels are noisy, and higher-fidelity free alternatives exist (a ~100k-market Kaggle set with trade data, a large HuggingFace tape, and recent large-scale academic datasets). It is a clean resolved-outcome base-rate layer reproducible from public data, not a moat.

Because the repository and this note are published regardless of outcome, reproduction is intended to be near-zero marginal effort for anyone wishing to re-run the twin mapping or extend it to additional metrics or venues.

Repository: `[REPO_URL]` · Dataset: `[DATASET_URL]` · Postmortem: `[POSTMORTEM_URL]`

## Conclusion

I set out to find a cross-venue edge and instead built a reasonably good machine for proving one is not there: pre-registered, fee-netted, spread-verified, freshness-filtered, convention-corrected, and adversarially audited against its own positives. The headline finding — that Polymarket and Kalshi agree wherever they genuinely co-list the same proposition, and co-list nothing where they might disagree — is a replication of an already-established efficiency literature, and I claim no novelty for it. The reusable part is the route: same-event identity, not price, is the hard problem in cross-venue work, and a matching pipeline that compares strike labels rather than reconstructed distributions will confidently report divergences that are not there. The five-artifact catalog and the distribution-comparison method are offered so that the next person measuring cross-venue divergence can reach the true answer faster, and trust it when they do.

## References

1. Ng, H., Peng, L., Tao, Y., & Zhou, D. (2026). *Price Discovery and Trading in Modern Prediction Markets.* SSRN Working Paper No. 5331995. — Cross-venue (Polymarket/Kalshi/PredictIt/Robinhood) price discovery around the 2024 U.S. election; Polymarket leads Kalshi under high liquidity. **[Confirm abstract ID, title, authors, and year on SSRN before submission — this entry could not be fetched directly.]**
2. Tsang, K. P., & Yang, Z. (2026). *The Anatomy of a Blockchain Prediction Market: Polymarket in the 2024 U.S. Presidential Election.* arXiv:2603.03136. — Efficiency maturation: arbitrage-deviation half-lives fall from hours to under a minute; Kyle's λ from 0.53 to 0.01.
3. Saguillo, O., Ghafouri, V., Kiffer, L., & Suarez-Tangil, G. (2025). *Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets.* arXiv:2508.03474; published at Advances in Financial Technologies (AFT) 2025, doi:10.4230/LIPIcs.AFT.2025.27. — Market-rebalancing vs combinatorial arbitrage on Polymarket; ~$40M estimated extracted.
4. Cheng, G., Yang, J., & Zou, H. (2026). *Arbitrage Analysis in Polymarket NBA Markets.* arXiv:2605.00864. — ~75M order-book snapshots across 173 games; mispricings structurally bounded by liquidity, confined to retail scale.
