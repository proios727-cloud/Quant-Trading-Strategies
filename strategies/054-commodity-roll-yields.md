---
rank: 54
slug: commodity-roll-yields
title: "Commodity Roll Yields"
asset_class: "futures / commodities"
style: "cross-sectional term-structure / backwardation"
horizon: "Monthly rebalance across commodity futures"
instruments: "listed futures"
---

# 054. Commodity Roll Yields

| Field | Value |
|---|---|
| Popularity rank (this kit) | 54 of 101 |
| Why it sits here | Erb–Harvey / Gorton–Rouwenhorst roll-yield sort. Long backwardated, short contango commodities. |
| Aliases | backwardation sort, term-structure carry, roll yield |
| Asset class | futures / commodities |
| Style | cross-sectional term-structure / backwardation |
| Typical horizon | Monthly rebalance across commodity futures |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A fully collateralized commodity future earns spot change plus roll as the contract slides down the curve. When the curve is backwardated the long earns positive roll; in contango the long pays roll and the short earns it. Rank commodities on the front/second-month price ratio and hold a zero-cost book: long high $\phi$, short low $\phi$.

You are not betting that oil goes up. You are betting that the term-structure premium is compensated across commodities. File 007 is time-series trend on each contract; this file is a cross-sectional sort on curve shape. File 089 is five-year spot value; this file is the nearby curve. File 055 uses COT positioning, not $\phi$.

Typical users are commodity risk-premium sleeves and CTA carry books. Horizon is monthly. Roll the held contract on the exchange calendar independently of the sort, and never hold into delivery. Delay-1: month-end $\phi$ trades the next close.

Energy often dominates the backwardated tail. Caps and inverse-vol weights exist so one WTI spike is not the whole book.

## 2. First principles

Let $P_1$ be the front-month future and $P_2$ the second-month future on the same commodity. The front/second ratio is

$$
\phi = \frac{P_1}{P_2}
$$

$\phi>1$ means $P_1>P_2$: backwardation. $\phi<1$ is contango. The ratio is unit-free, so gold and corn can be ranked together. Using $P_1-P_2$ in dollars would let the high-priced metal dominate the sort. Missing $P_2$ means you cannot see the curve; drop the name rather than filling $\phi=1$.

Holding the front and rolling into the next contract harvests a roll yield whose sign tracks $\phi-1$. Under a static curve the roll over one month is on the order of $\ln\phi$ (or $(P_1-P_2)/P_2$). That static-curve story is the same idea as bond roll-down, applied to commodity calendars. A long-only index that always holds the front therefore bleeds in a contango market. The cross-section flips that: long the backwardated names, short the contango names, dollar-neutral.

That is the whole strategy. Everything below is the sort, the weights, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | commodities after liquidity filters |
| $P_1, P_2$ | front and second month futures prices |
| $\phi_i = P_{1,i}/P_{2,i}$ | backwardation if $\phi_i>1$ |
| $R_i$ | futures excess return over the holding bar (variation margin / notional) |
| $w_i$ | signed weights, $\sum_i w_i=0$ and $\sum_i\lvert w_i\rvert=1$ |
| $I$ | gross notional |
| $D_i = w_i I$ | signed notional in commodity $i$ |

## 4. Mathematics

### 4.1 Roll signal

On each commodity, using closes dated $\le t < t_{\mathrm{fill}}$:

$$
\phi = P_1 / P_2
$$

$\phi>1$ backwardation, $\phi<1$ contango. Missing $P_2$ → drop the name and resort. $P_1$ and $P_2$ must be the same commodity and the same as-of date. Mixing a nearby calendar spread from $t+1$ into $\phi_t$ is look-ahead. Identify front and second on a point-in-time roll calendar, not on today’s knowledge of a later Goldman-roll date.

### 4.2 Cross-sectional book

Zero-cost: long high $\phi$, short low $\phi$. Default: terciles or deciles depending on $N$. Equal-weight inside each tail, or inverse-vol weights using a trailing $\sigma_i$ that ends at $t$.

$$
\sum_i w_i = 0, \qquad \sum_i \lvert w_i\rvert = 1
$$

Dollar-neutral plus gross-one is the budget. After ADV clipping you must restore both identities or park the residual in a notional bucket. Sign: $w_i>0$ on the high-$\phi$ tail, $w_i<0$ on the low-$\phi$ tail, $w_i=0$ in the middle. A long-only “buy backwardation” book is a different spec: it keeps the spot beta this file is trying to cancel.

### 4.3 Holding-period P&L

Futures P&L is marked daily on variation margin; no full notional cash outlay. Include roll P&L when the front is switched:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$R_i^{\mathrm{fwd}}$ is the excess return of the contract you actually held, including the roll from $P_1$ into the next front. If the engine always marks a constant-maturity series that you did not trade, the P&L is not this book. Report return on gross $I$, Sharpe on **non-overlapping** months, and one-way turnover.

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

Monthly sorts already turn over when $\phi$ ranks flip. Daily resorting of a slow curve signal is mostly cost.

## 5. Step-by-step algorithm

1. **Universe.** Listed commodity futures with both a liquid front and a liquid second month. Exclude markets in delivery. This step exists because a delivery-month “front” is not a curve signal you can hold, and financial futures (equity, rates, FX) are out of this file unless explicitly extended.
2. **Contracts.** One front-month (or constant-maturity) future per commodity. Identify $P_1,P_2$ on a point-in-time roll calendar. A roll date that was not public at $t$ cannot choose the $t$ front.
3. **Signal.** $\phi_i=P_{1,i}/P_{2,i}$ from stamps $\le t$. Drop missing $\phi$; do not impute 1.
4. **Sort.** High $\phi$ → long tail; low $\phi$ → short tail. Drop missing $\phi$. The sort is the only alpha. Mixing COT or 5-year value into $\phi$ is a different factor.
5. **Weights.** Equal or inverse-vol inside tails; renormalize to $\sum w_i=0$, $\sum\lvert w_i\rvert=1$. Inverse-vol uses a window ending at $t$, not the holding month.
6. **Caps.** Clip by ADV / open interest. Restore neutrality after clipping. Energy names will otherwise eat the book.
7. **Blotter.** Convert notionals to contracts, round, emit intents. Do not route live orders. Rounding that drops the short tail leaves a long-only commodity bet.
8. **Rebalance.** Monthly. Roll the held contract independently of the sort, before delivery. The sort says which commodity; the calendar says which expiry.

## 6. Execution protocol

- Default fill: next close after $\phi$ is known (month-end signal, next-day or next-month fill). Delay-0 is research-only.
- Roll independently of the sort. Exclude markets in delivery.
- Do not mix in financial futures (equity, rates, FX) unless the file is explicitly extended; this spec is commodities.

## 7. Data contract

Required, point-in-time:

- Generic or contract-level futures prices for front and second month
- Volume, open interest, delivery/roll calendar
- Term structure stamps used to build $\phi$

Not used by this spec: CFTC COT (that is 055), 5-year spot value (that is 089), equity book value, earnings, SUE.

No look-ahead on rolls. A Goldman-roll date must be known before the fill that uses it. Restated generic series that rebuild history after a roll-rule change must not leak into $t$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| sort | terciles or deciles | depends on $N$ |
| weights | equal inside tails | inverse-vol allowed |
| rebalance | monthly | |
| delivery | exclude | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.commodity_roll_yields` with:

1. `phi(P1, P2) -> pd.Series` — $\phi=P_1/P_2$, no look-ahead.
2. `weights(phi, I, vol=None, q=3) -> pd.Series` — $w_i$ with $\sum w_i=0$ and $\sum\lvert w_i\rvert=1$ to `1e-8`.
3. `blotter(weights, prices, I, lot, calendar) -> list[OrderIntent]` — contracts, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — includes roll, matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Curve inversion.** Backwardation can flip in a glut; the long tail becomes the bleed. $\phi$ is not a clock that the glut ends this month.
- **Crowded index rolls.** Calendar rolls (Goldman roll) are anticipated. Trading the same roll as the index on the same day is impact, not alpha.
- **Sector concentration.** Energy often dominates the backwardated tail. Without caps, the factor is a disguised WTI book.
- **Delivery.** Holding into delivery is not this spec. First-notice filters exist so you do not “earn” a physical delivery P&L in a paper book.
- **Missing second month.** Filling $\phi=1$ parks illiquid names in the middle; dropping them and resorting is required.
- **Look-ahead roll calendar.** Using a later generic definition to pick $P_1$ at $t$ restates the signal.

## 11. Acceptance tests

- $\phi=P_1/P_2$ to `1e-8`. $\phi>1$ names sit in the long tail, $\phi<1$ in the short tail, on a three-name toy that spans both.
- $\sum w_i=0$ and $\sum\lvert w_i\rvert=1$ to `1e-8`.
- Permuting $P_1,P_2$ after $t$ must not change $\phi_t$.
- A name in delivery is absent from $w$, not zero-filled as a tradable.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
