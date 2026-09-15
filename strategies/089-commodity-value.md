---
rank: 89
slug: commodity-value
title: "Commodity Value"
asset_class: "futures / commodities"
style: "long-horizon mean-reversion / value"
horizon: "Monthly rebalance, slow signal"
instruments: "listed futures"
---

# 089. Commodity Value

| Field | Value |
|---|---|
| Popularity rank (this kit) | 89 of 101 |
| Why it sits here | Asness–Moskowitz–Pedersen commodity value: 5-year spot vs today. |
| Aliases | commodity long-run reversal, AMP value |
| Asset class | futures / commodities |
| Style | long-horizon mean-reversion / value |
| Typical horizon | Monthly rebalance, slow signal |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Commodities that are depressed versus their own five-year history are “cheap” on a long-horizon mean-reversion measure. Value is $v=P_5/P_0$: spot five years ago over spot today. Long high $v$, short low $v$, terciles, monthly rebalance. Slow: do not overtrade.

You are not sorting on front/second $\phi$ (file 054), not on COT (file 055), and not fading last week (file 056). You are ranking five-year drawdowns in spot (or a documented nearby-future proxy). Combining $v$ with momentum is a multifactor kit, not a change in $v$.

Typical users are slow commodity factor sleeves inside a multi-asset value book. Horizon is monthly on a five-year signal: $v$ barely moves week to week, so weekly rebalances are cost. Names with less than the required history are dropped, not filled with $v=1$. Delay-1: month-end $v$ trades the next close. Document whether $P$ is cash spot or nearby future; mixing them inside one name embeds roll into “value” and then you are partly running file 054 without saying so. Sector caps matter: one energy complex can fill an entire tercile after a five-year bear market.

## 2. First principles

Let $P_0$ be today’s spot (or a documented nearby-future proxy) and $P_5$ the spot five years ago. The ratio

$$
v = \frac{P_5}{P_0}
$$

is large when the commodity has fallen a lot over five years and small when it has rallied. A halved price doubles $v$ versus an unchanged name. Ranking on $P_0-P_5$ in dollars would let high-priced metals dominate. $P_5$ must be dated five years before $t$, not five years before $t+1$.

Long-horizon mean-reversion says real prices of commodities tend to pull back toward a slow mean (inventories, substitution, new supply). Ranking on $v$ is then a cross-sectional value book: long the depressed names, short the elevated names. A dying commodity can stay depressed; $v$ stays high. That is structural cheapness, not a clock.

$P_5$ may be a point print five years ago or an average of spot from 5.5 years to 4.5 years ago (smoother). $P_0$ is current spot. Trade the liquid future, not the cash commodity, and include roll in P&L. Spot versus futures basis is tracking error if $P_0$ was cash spot.

That is the whole factor. Everything below is the tercile book, the spot-proxy rule, and how not to look ahead. If you skip the five-year history requirement and fill $v=1$, new contracts park in the middle and distort cuts. If you skip the zero-cost constraint, a long-only “buy cheap commodities” book is a residual-long sector bet. If you skip documenting the spot proxy, roll yield leaks into $v$ and you can no longer tell value from file 054.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | commodities |
| $P_0$ | current spot (or nearby-future proxy) |
| $P_5$ | spot 5 years ago, or average from 5.5y to 4.5y ago |
| $v=P_5/P_0$ | value score |
| $R_i$ | futures excess return over the holding month |
| $w_i$ | signed weights, $\sum_i w_i=0$, $\sum_i\lvert w_i\rvert=1$ |
| $I$ | gross notional |
| $D_i=w_i I$ | signed notional |

## 4. Mathematics

### 4.1 Value score

Using only stamps $\le t$:

$$
v = P_5 / P_0
$$

$P_5$ = spot 5 years ago (or average spot from 5.5y to 4.5y ago). $P_0$ = current spot. High $v$ → long; low $v$ → short. Restated spot history (index revisions) must not leak into $t$. If $P_0\le 0$, the name is missing, not infinite value.

### 4.2 Book

Long top tercile, short bottom tercile. Equal-weight inside tails, then

$$
\sum_i w_i = 0, \qquad \sum_i \lvert w_i\rvert = 1
$$

Monthly rebalance. Do not churn inside the month: $v$ is slow. Daily resorting a five-year ratio is turnover without information. Inverse-vol inside tails is allowed if $\sigma_i$ ends at $t$.

### 4.3 Holding-period P&L

Futures variation margin, including roll, minus costs:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Spot versus futures basis is tracking error if $P_0$ was a cash spot and the trade is a future. Report return on $I$, Sharpe on **non-overlapping** months, and turnover. $R_i^{\mathrm{fwd}}$ is the future you held, including the roll calendar, not the spot change in $P_0$.

## 5. Step-by-step algorithm

1. **Universe.** Listed commodity futures with a consistent spot series (or nearby futures as the spot proxy, documented). This step exists so gold cash versus gold generic futures are not mixed inside one $v$.
2. **Spot.** Build $P_0$ and $P_5$ from the same series, point-in-time, no restatement. $P_5$ is dated five years before $t$.
3. **Score.** $v_i=P_{5,i}/P_{0,i}$. Drop missing history (need ~5 years). Do not fill $v=1$.
4. **Sort.** Terciles: long high $v$, short low $v$. Middle is flat.
5. **Weights.** Zero-cost, equal or inverse-vol. Restore neutrality after ADV caps.
6. **Contracts.** Trade the front liquid future; roll on the calendar, independent of $v$. The signal is slow; the contract is not.
7. **Blotter.** Contracts from $D_i$, round, emit intents. Do not route live orders.
8. **Rebalance.** Monthly. Delay-1. Weekly $v$ updates are noise.

## 6. Execution protocol

- Default fill: next close after month-end $v$. Delay-0 is research-only. Using the fill-day spot in $P_0$ mixes the first holding-period move into the signal.
- Slow: do not overtrade. Combining with momentum (054-style roll or a 12-1 return) is a multifactor kit, not a change in $v$. If you blend them, keep $v$ as its own series in the logs.
- Document whether $P$ is cash spot or nearby future. Mixing them inside one name is a failed spec. A nearby-future $P_5$ that itself rolled for five years is not the same object as cash spot.

## 7. Data contract

Required, point-in-time:

- A consistent spot series (or nearby-future proxy) with at least 5.5 years of history
- Contract-level futures for trading, volume, open interest, roll calendar

Not used by this spec: COT HP (055), front/second $\phi$ as the signal (054), equity book value, earnings, SUE.

No look-ahead on $P_0$. $P_5$ is dated five years before $t$, not five years before $t+1$. A revised historical spot index that rewrites $P_5$ after $t$ does not change $v_t$. If the spot series has gaps, drop the name for that month rather than interpolating across a missing year, which would invent a smooth mean-reversion path that was not on the tape.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| window | 5 years | or 5.5y–4.5y average |
| sort | terciles | |
| rebalance | monthly | slow |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.commodity_value` with:

1. `value(P5, P0) -> pd.Series` — $v=P_5/P_0$, no look-ahead.
2. `weights(v, I, q=3) -> pd.Series` — tercile book, $\sum w_i=0$, $\sum\lvert w_i\rvert=1$ to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — futures, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — includes roll.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Structural cheapness.** A dying commodity can stay depressed; $v$ stays high. Five-year mean reversion is not a promise of a bounce this month.
- **Spot vs futures.** Proxying $P$ with a future that rolls embeds carry into “value.” Then $v$ mixes file 054 into this file.
- **Sector concentration.** One complex can dominate a tercile. Caps exist because of that.
- **Gaps.** Thin contracts gap on the monthly fill.
- **Short history.** Filling missing $v$ with 1 parks new contracts in the middle and distorts terciles.
- **Look-ahead $P_0$.** Using next month’s spot in this month’s $v$ is the holding return.

## 11. Acceptance tests

- $v=P_5/P_0$ to `1e-8`. A name with halved price over five years has twice the $v$ of an unchanged name, other things equal.
- Tercile toy: highest $v$ long, lowest $v$ short, middle flat.
- Permuting spots after $t$ must not change $v_t$.
- Names with less than the required history are dropped, not filled with $v=1$.
- Adding linear costs $\tau$ weakly decreases P&L.
- Mixing cash spot for $P_5$ with a nearby future for $P_0$ on the same name must be rejected unless the run documents a single proxy series.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
