# When the Negative Result *Is* the Result: A Postmortem on PolyEdge

> A solo, ~$406 attempt to build a profitable prediction-market trading bot, why I retired the trade, the data-product pivot that followed, and the rigorously-measured negative result that ended it. Written for people who might try something similar — so they can skip the parts that don't work.

**Repository:** https://github.com/mstover-creator/prediction-market-twins · **Dataset (DOI):** https://doi.org/10.5281/zenodo.20849433 · **License:** MIT (code), CC-BY-4.0 (data)

## The result, first

**There is no edge here, and I can prove it.**

Three independent measurements killed three independent theses:

1. **LLM directional signal is dead.** Experiment E-17 (n=540, p=2.3e-49) showed that LLM-derived directional predictions against live Polymarket prices have no exploitable signal. Not "weak." Signal-dead, at a significance that leaves no room for "more data will help."
2. **Fee structure kills mechanical arbitrage.** The cross-venue price gap exists (~1.5 points where it exists at all), but Polymarket's 2026 dynamic taker fee eats ~94% of it. A blind taker strategy lands at ~coin-flip and is scale-invariant in the wrong direction.
3. **Cross-venue divergence is not a product — and this is the subtle one.** After building an instrument to detect Polymarket↔Kalshi price disagreements on the same event, and testing it *both* on Polymarket-International *and* on the apples-to-apples Polymarket-US (same CFTC jurisdiction as Kalshi), the finding is clean and, I believe, generalizable: **wherever the two venues genuinely list the same resolvable proposition in volume, their prices agree to within noise; wherever they might disagree, they don't list the same proposition.** There is no regime that gives you both real twins *and* a persistent, beyond-spread gap.

If you came here for a strategy, that's it: the strategy is to not run this strategy. The rest of this document is about *how* I know that, because the methodology is the only thing here worth keeping.

## The arc

PolyEdge started as a Polymarket trading bot. The setup was modest and a little absurd: ~$406 of working capital, a single 4GB VPS, one operator, and — because Polymarket is geoblocked in the US — all trading traffic egressing through an Ireland WireGuard tunnel. The bot evaluated markets on a loop, asked an LLM where price "should" be, consulted a RAG corpus of historical resolutions for base rates, and placed trades through Polymarket's CLOB API.

It lost money. The interesting part is not that it lost money — most retail trading bots do — but that I stopped, instrumented *why*, and let the measurement make the decision instead of my hope.

## Why trading was retired

**The LLM had no directional edge (E-17).** The original thesis was that a reasoning LLM, fed news and base rates, could price binary event markets better than the market itself. I ran it as a pre-registered experiment rather than a vibe. The verdict at n=540 was p=2.3e-49 against any signal — no positive sub-slice at high confidence, large stated edge, or any category. The market price already integrates everything the model "knows"; the apparent edge was noise that vanished the moment it was scored against realized outcomes instead of against itself.

**Fees killed arbitrage independently.** The fallback was mechanical, not predictive: buy YES on one venue, NO on the other, when the implied sum < $1. The gap is ~1.5 points where it exists; the 2026 dynamic taker fee eats ~94% of it. Maker orders dodge the fee (and can earn rebate) but introduce legging risk — fill one side, hang on the other — which on $406 is not a risk you can warehouse.

Every path was net-negative at this capital level. So I retired trading. **I am not going to resume it, and if you are reading this looking for the version where the edge was real, there isn't one.**

## The pivot: sell the instrument, not the trades

Retirement left behind something real: a working, real-time, multi-venue market-data engine (`polyedge-tape.service`). The pivot thesis: even if *trading* the data doesn't pay, the *infrastructure and the measurements* might — as open data products and as a credible artifact for a venue Builders grant. The one signal a single-venue scraper structurally **cannot** reproduce is **cross-venue divergence**: Polymarket and Kalshi disagreeing on the same event at the same moment. If that disagreement were real, persistent, and fee-clearing, it would be at minimum an interesting public dataset. So I built an instrument to measure it honestly — and then spent most of my effort trying to *disprove* my own positives.

## The instrument

Built with the same discipline that produced the clean E-17 negative:

- **Pre-registration, sha256-frozen.** Success criteria, era tag, and scoring rules were written down and hashed *before* collecting evaluation data. You cannot move goalposts that are hashed.
- **Three-stage twin mapping.** Matching "the same event" across venues is the hard part and where wishful matching creeps in: (1) a *structural date gate* (resolution windows that can't overlap can't be twins); (2) a *budgeted LLM recognition* pass (does this PM market describe the same real-world event as this Kalshi one?) — budgeted because LLM calls cost money and I had ~$406; (3) a *price-geometry polarity veto* (genuine twins must move with consistent polarity; if the geometry disagrees, reject regardless of what the LLM thought).
- **Fee-netting + spread-verification.** A gap is only "tradeable" after netting taker fees and measuring against real bid/ask, not midpoints.
- **Both-legs-active / freshness filter.** The filter I most want a future builder to copy. Many apparent gaps were **liquidity artifacts** — one venue's quote *frozen* (in one case stale ~30 hours), so the "divergence" was one leg failing to update, not two markets disagreeing.

## The negative result, in two acts

### Act 1 — Polymarket-International: same-event overlap is rare

Running across politics, macro, geopolitical, climate, tech, and crypto, the overlap that survived honest twin-matching collapsed to **named, discrete political/geopolitical questions** ("will person P win nomination N"). Everything else — crypto, climate, macro — is *carried* by both venues but *specified differently* (different strikes, timestamps, resolution sources), so "same theme" never becomes "same event." Net publishable overlap on PM-Intl was a thin handful of named-entity pairs. Suggestive, but not a dataset, a product, or a grant flagship — and open to the objection: *maybe you used the wrong Polymarket.*

### Act 2 — Polymarket-US: the apples-to-apples test, and the real answer

That objection deserved a real test. Polymarket launched a **US, CFTC-regulated** venue (QCEX) — same jurisdiction as Kalshi. I rebuilt the instrument against it (Ed25519-signed REST/WS, per-outcome slug handling) so the comparison was apples-to-apples. The result splits cleanly by market *type*:

- **Politics:** 82 LLM mapping attempts, **0 confirms.** PM-US is granular (per-candidate primaries, per-district, "midterm winner") while Kalshi lists party-wins-the-general at a different year — same nouns, different resolvable question.
- **Sports:** **0/15** even find a candidate. The two venues list *different kinds* of sports markets (PM season-futures + method-of-victory props; Kalshi novelty/championship futures), not the same dated games.
- **Scalar ladders — the place twins genuinely exist *in volume*:** daily city high-temperature, and monthly macro prints (unemployment, GDP, payrolls, CPI, Fed). A targeted fetch found **4,251** Kalshi scalar markets against PM-US's daily weather and macro ladders. *Here there really are many twins.* And here is the punchline:

**Once parsed correctly, the venues agree.** Implied-median gaps: Chicago high 0.01°F, Miami 0.05°F, NYC 0.07°F, LA 0.11°F; US Q2 GDP 0.06pp; US June unemployment ~0.001pp (convention-adjusted). Kalshi spreads were 1.5–6pt — liquid markets genuinely agreeing, not frozen legs.

### Why every "signal" along the way was an artifact (the catalog)

This is the most transferable part of the document. Each of these *manufactured* a phantom edge that a naive analyst would have published:

- **≥ vs > convention.** PM uses inclusive `≥X` ("gte"/"atl"); Kalshi uses strict `>X` ("above"). For data reported to one decimal, Kalshi ">4.3%" *equals* PM "≥4.4%" — a one-tick offset that fabricated a ~12-point "divergence" across every macro print. Align the convention and the gap collapses to ~2pt.
- **Bands vs tails.** PM weather is *bands* (`72–73°`); Kalshi is *tails* (`above 72°`). Comparing the raw strike labels is comparing different objects.
- **Series contamination.** Keying twins on (city, date) merged three *different* Kalshi metrics — daily-high (`KXHIGH`), daily-low (`KXLOWT`), and 2pm-instantaneous (`KXTEMP`) — into one curve, dragging the implied "median" ~14°F and producing a fake 98pt probability gap. The metric is encoded in the series ticker; you must split on it.
- **Subject collapse.** Defaulting every macro market to "US" merged US + Italy + Germany + France GDP (YoY *and* QoQ) into a single comparison. Garbage by construction.
- **Sign-dropping + overround.** A regex that ate the leading minus folded negative GDP strikes onto positive ones; and PM's ladders are ~26% *overround* (probabilities summing to ~1.26 — LLM/illiquid-priced), so per-bin probabilities are noisy. The implied **median** (the distribution's *location*) is the only statistic robust to all of this.

### The correct method, in one sentence

**Don't compare strike labels — reconstruct each venue's implied distribution for a (metric, subject, reference-period) twin and compare the curves (implied median / survival function).** That is the single change that turns phantom 14°F/98pt "signals" into the true ~0.1°F agreement.

### How I know it's not just my own bug

Because the *first* version of the scalar measurement reported a 14°F weather "edge," and that smelled exactly like the convention/freshness artifacts that had fooled me before, I ran the suspicious result through an **adversarial multi-agent audit** — independent agents each re-deriving a twin by hand from the raw data, plus a skeptic tasked with proving it was an artifact. All four converged on *signal-is-real = false* and named the bugs above; a corrected end-to-end re-measurement then reproduced the ~0.1°F agreement across the whole twin universe. The discipline that produced the clean negative is the same discipline that refused to let a buggy positive survive.

## What I'd tell someone considering this

- **Pre-register before you collect, and hash the file.** Both clean negatives (E-17, the divergence gate) only count because the target was fixed in advance.
- **Build the freshness / both-legs-active filter first, not last.** Stale quotes hand you fake alpha all day.
- **Net fees before you get excited.** A 2026 dynamic taker fee can eat ~94% of a real gap.
- **In cross-venue work, the hard problem is *same-event identity*, not price.** "Same topic" is common; "same spec-identical, same-period proposition" is rare — and is where the entire opportunity would have to live.
- **Watch the conventions: ≥ vs >, bands vs tails, inclusive vs strict, units, series.** Each one silently manufactures a divergence that isn't there. Compare *distributions*, not strike labels.
- **A small bankroll changes which strategies are even legal.** Legging and warehousing risk a fund shrugs off are fatal at $406.
- **Adversarially verify your own positives.** I trust this negative result precisely because I spent more effort trying to kill the positives than to confirm them.
- **Let the measurement make the call.** I wanted every thesis to work. They didn't, and the instrument said so before my ego did. That's the win condition.

## What's open-sourced

- **The instrument** — the cross-venue divergence watcher (structural date gate → budgeted LLM recognition → price-geometry polarity veto), fee-netting, spread-verification, the freshness filter, and the pre-registration/freezing harness; plus the **scalar-twin measurement** (distribution reconstruction, convention handling, the artifact-catalog gates) and the **multi-agent adversarial audit** that validated it.
- **The postmortem** — this document, including the frozen pre-registration target and *why* it was structurally unreachable.
- **A cleaned corpus slice** — 462,285 resolved Polymarket binary markets (`token_id`, `question`, `slug`, `resolved_yes`, `resolved_at`, `volume`, `volume24hr`, `liquidity`, `end_date`, `category`), 2022-08 → 2026; 37.3% YES base rate across ~395,411 distinct questions.

**Honest caveats on the corpus, up front:** `volume`/`volume24hr`/`liquidity` are 100% zero (never captured — treat as absent). `category` labels are noisy (NCAAB tagged `crypto`; the largest bucket, ~162k rows, is `other`). It's sourced from the public Gamma API + on-chain CTF resolutions, so it's **fully reproducible from public data**, and higher-fidelity free alternatives exist (a ~100k-market Kaggle set *with* trading data; a 107GB HuggingFace dump). The value is the cleaned, normalized resolved-outcome layer and the base rates — **not** a moat. It's offered as a convenience and a citation target.

## The close

PolyEdge is winding down to a clean, honorable stop. There is no remaining income thesis — trading is dead three ways, and cross-venue divergence, tested apples-to-apples and at scale, is not a product: where the venues co-list the same proposition they agree, and where they might disagree they don't co-list it. What remains has value but is not a business: the corpus is published, the instrument and methodology are open-sourced, this postmortem ships, and the tape keeps running as an autonomous demo for ~60 days before it closes.

I set out to find an edge and instead built a fairly good machine for proving an edge isn't there — pre-registered, fee-netted, spread-verified, freshness-filtered, convention-corrected, and adversarially audited against its own positives. The trades were a dead end. The discipline wasn't.
