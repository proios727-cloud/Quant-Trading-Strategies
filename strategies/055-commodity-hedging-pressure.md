---
rank: 55
slug: commodity-hedging-pressure
title: "Trading Based on Hedging Pressure"
asset_class: "futures / commodities"
style: "COT positioning / hedgers vs speculators"
horizon: "Formation and hold ~6 months"
instruments: "commodity futures; CFTC COT positioning"
---

# 055. Trading Based on Hedging Pressure

| Field | Value |
|---|---|
| Popularity rank (this kit) | 55 of 101 |
| Why it sits here | CFTC COT hedging-pressure signal. Classic commodity risk-premium overlay. |
| Aliases | COT hedge pressure, commercial positioning |
| Asset class | futures / commodities |
| Style | COT positioning / hedgers vs speculators |
| Typical horizon | Formation and hold ~6 months |
| Instruments | commodity futures; CFTC COT positioning |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Commercial hedgers transfer commodity price risk to speculators. When hedgers are net short, they pay for insurance and the curve tends to backwardation; when they are net long, the opposite. Measure hedging pressure as longs / (longs + shorts) in the CFTC COT report, separately for hedgers and speculators, and build a slow zero-cost futures book from those ranks.

You are taking the speculator’s side of a slow imbalance, not trading $\phi$ (file 054) and not fading last week’s return (file 056). COT buckets are messy labels, not a clean “hedger versus speculator” partition. The report used at $t$ must have been public before the fill. Using the snapshot Friday as if it were public is look-ahead and a failed spec.

Typical users are commodity risk-premium books that can wait. Formation and hold are about six months. Weekly COT still does not mean weekly trading: the double sort is slow. Delay is next close after the public release.

## 2. First principles

Keynes–Hicks: the side that must hedge pays a premium to the side that can warehouse the risk. Define hedging pressure on a group (commercials / non-commercials) as the share of long open interest in that group:

$$
\mathrm{HP} = \frac{\mathrm{longs}}{\mathrm{longs}+\mathrm{shorts}} \in [0,1]
$$

$\mathrm{HP}=1$ means that group is entirely long; $\mathrm{HP}=0$ means entirely short. Spreading positions are excluded from this HP unless the caller documents otherwise. Mixing legacy COT with disaggregated COT without a field map will relabel the same name from “hedger” to “managed money” and invert the book.

High **hedger** HP means commercials are tilted long (they are buying protection against a price fall, typical of inventory holders who are short the physical in an accounting sense, or consumers who are long the physical need — document the COT map). Empirically, high hedger HP lines up with contango; high **speculator** HP lines up with backwardation.

The trade is to take the speculator’s side of the imbalance, slowly: long commodities where speculators are already long and hedgers are short, short the opposite. COT is weekly and lagged; the report used at $t$ must have been public before the fill.

That is the whole strategy. Everything below is the double sort, the 6-month hold, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | commodity futures in the universe |
| $\mathrm{HP}^{\mathrm{hedge}}_i$ | commercial hedging pressure in $[0,1]$ |
| $\mathrm{HP}^{\mathrm{spec}}_i$ | non-commercial (speculator) hedging pressure in $[0,1]$ |
| $R_i$ | futures excess return over the holding window |
| $w_i$ | signed weights, $\sum_i w_i=0$ and $\sum_i\lvert w_i\rvert=1$ |
| $I$ | gross notional |
| $D_i=w_i I$ | signed notional |

## 4. Mathematics

### 4.1 Hedging pressure

For each commodity and each COT group, using only reports published before $t_{\mathrm{fill}}$:

$$
\mathrm{HP} = \frac{\mathrm{longs}}{\mathrm{longs}+\mathrm{shorts}}
$$

Document the field map: commercials = hedgers, non-commercials = speculators (or the disaggregated COT analogue). Spreading positions are excluded from this HP unless the caller documents otherwise. If longs+shorts is zero, the name is missing, not $\mathrm{HP}=0.5$. Publication timestamp, not snapshot date, is the clock that feeds the lag check.

### 4.2 Double sort

Construction:

1. Split names into upper/lower half by speculator HP.
2. Long the upper half if they sit in the **bottom** quintile of hedger HP.
3. Short the lower half if they sit in the **top** quintile of hedger HP.

Names that fail the second screen are flat. The surviving longs and shorts form a zero-cost book: equal-weight (or inverse-vol) inside each side, then rescale to $\sum\lvert w_i\rvert=1$ and $\sum w_i=0$. Formation and hold typically 6 months. The two screens exist so you do not long every name speculators like, including those where hedgers are not actually paying. A single-sort on speculator HP is a different spec.

### 4.3 Holding-period P&L

Futures variation margin over the hold, including rolls, minus costs:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Report return on $I$, Sharpe on **non-overlapping** 6-month holds, and the publication lag used. Overlapping 6-month windows will make a weekly COT series look like dozens of independent bets. Rolls follow the futures calendar, not the COT Friday.

## 5. Step-by-step algorithm

1. **Universe.** Liquid commodity futures with a complete COT series. Exclude delivery months. This step exists because a name without COT cannot have HP, and delivery months are not a 6-month hold.
2. **COT map.** Freeze the commercial / non-commercial (or producer/merchant vs managed money) field map. Silent swaps of legacy for disaggregated COT invert labels.
3. **Lag.** Align so the report used at $t$ was public before the trade. Typical: Friday snapshot, released the following Friday; trade on the next close after release. This step is the look-ahead gate. Snapshot Friday fills are research-only and fail the spec.
4. **HP.** Compute $\mathrm{HP}^{\mathrm{hedge}}$ and $\mathrm{HP}^{\mathrm{spec}}$ on that report. Do not mix weeks across names to “complete” a panel.
5. **Sort.** Apply the median speculator split and the hedger quintile screens in 4.2. Names that fail are flat, not interpolated into a tail.
6. **Weights.** Zero-cost, equal or inverse-vol on survivors. If one side is empty, the book is flat or the surviving side is not run unpaired; do not keep a one-sided commodity bet.
7. **Blotter.** Contracts from $D_i$, round, emit intents. Do not route live orders.
8. **Hold.** ~6 months, then resort. Roll contracts independently of the sort. Weekly COT updates during the hold do not force a rebalance unless a separate variant says so.

## 6. Execution protocol

- COT is weekly and lagged. Never use a report before its public timestamp.
- Default fill: next close after the public release. Delay-0 on the snapshot Friday is research-only and look-ahead.
- Document the COT field map in the run config; do not silently swap legacy COT for disaggregated COT.

## 7. Data contract

Required, point-in-time:

- CFTC COT (legacy or disaggregated), with **publication** timestamps
- Generic or contract-level futures prices, volumes, open interest
- Roll/delivery calendar

Not used by this spec: front/second $\phi$ as the signal (that is 054; $\phi$ may be logged as a diagnostic), 5-year spot value, equity book value, earnings, SUE.

No look-ahead on unreleased COT. A restated historical COT file that revises old longs and shorts must not change the $t$ book unless that revision was public at $t$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation / hold | 6 months | |
| speculator split | median | upper vs lower half |
| hedger screen | bottom / top quintile | long / short |
| COT lag | public timestamp | never snapshot date alone |
| delay | next close after release | |

## 9. Agent implementation contract

Build a Python module `strategies.commodity_hedging_pressure` with:

1. `hedging_pressure(longs, shorts) -> float` — $\mathrm{HP}\in[0,1]$.
2. `signal(hp_hedge, hp_spec, t_pub, t_fill) -> pd.Series` — signed scores from the double sort; refuse $t_{\mathrm{pub}}\ge t_{\mathrm{fill}}$.
3. `weights(signal, I, vol=None) -> pd.Series` — $\sum w_i=0$, $\sum\lvert w_i\rvert=1$ to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — contracts, never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Classification noise.** COT buckets are not clean “hedger vs speculator.” Producer/merchant versus swap dealers versus managed money will not match the legacy split.
- **Crowding.** The same weekly print is public to everyone. Capacity shows up as the fill moving after the release, which delay-1 already assumes.
- **Lag.** A 6-month hold on a weekly signal is slow; regimes can flip inside the hold. Tightening to a 1-week hold is a different spec.
- **Look-ahead.** Using the snapshot Friday as if it were public is a failed spec. Tests must refuse $t_{\mathrm{pub}}\ge t_{\mathrm{fill}}$.
- **One-sided survivors.** If the short screen is empty, running only the longs is a residual-long commodity book.
- **Delivery.** Holding a COT signal into first notice is still a delivery problem.

## 11. Acceptance tests

- $\mathrm{HP}=\mathrm{longs}/(\mathrm{longs}+\mathrm{shorts})$ in $[0,1]$ to `1e-8`.
- A name in the speculator upper half and hedger bottom quintile is long; speculator lower half and hedger top quintile is short; others flat on a toy cross-section.
- Feeding a COT report with $t_{\mathrm{pub}}\ge t_{\mathrm{fill}}$ must not change the $t_{\mathrm{fill}}$ book (the report is ignored).
- $\sum w_i=0$ and $\sum\lvert w_i\rvert=1$ on the survivors.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
