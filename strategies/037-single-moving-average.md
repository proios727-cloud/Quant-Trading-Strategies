---
rank: 37
slug: single-moving-average
title: "Single Moving Average"
asset_class: "equities"
style: "single-name trend / technical"
horizon: "Daily. Position held while price stays on the same side of the MA."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 037. Single Moving Average

| Field | Value |
|---|---|
| Popularity rank (this kit) | 37 of 101 |
| Why it sits here | Price vs MA (e.g. 50-day, 200-day). The simplest widely used trend overlay, including the dual-momentum filter. |
| Aliases | price vs MA, MA overlay |
| Asset class | equities |
| Style | single-name trend / technical |
| Typical horizon | Daily. Position held while price stays on the same side of the MA. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long (cover) if price is above $\mathrm{MA}(T)$; short (sell) if below. Long-only, short-only, or two-way. Multi-name signals are independent. The book is near dollar-neutral only if it happens to split. The 200-day SMA on an index is the usual dual-momentum risk-off switch.

You are betting that price sitting above its own local mean is a continuation of drift, not a forecast of a target. You hold the **sign** of $P-\mathrm{MA}(T)$ until price crosses back. You are not ranking names, not targeting dollar-neutrality, and not running dual MA — dual MA ([`004-two-moving-averages.md`](004-two-moving-averages.md)) replaces $P$ with a shorter average.

You are also not claiming a high-Sharpe one-name equity factor. Typical user: a dual-momentum overlay (long the index only when $P>\mathrm{SMA}(200)$), or a chartist automating 50-day / 200-day price vs MA. Horizon intuition: daily bars; a 50-day rule holds weeks; a 200-day rule holds months. Sideways tape through the MA is the failure mode.

If you put the fill bar inside the MA, or use unadjusted prices, the backtest is an optimistic or split-broken cousin of this spec.

## 2. First principles

A moving average is a local estimate of the price level. Index bars so that $t=1$ is the most recent bar **in the MA sample** and $t$ increases into the past. The simple moving average of length $T$ is

$$
\mathrm{SMA}(T) = \frac{1}{T}\sum_{t=1}^{T} P(t)
$$

Equal-weight level on the last $T$ adjusted closes in the sample. Under delay-1, that sample ends before the fill, so $t=1$ is yesterday, not the fill bar. This is a level, not a return. A split without adjustment halves $P$ and looks like a crash through the MA. Trading before $T$ bars exist is not an SMA($T$).

The exponential moving average of length $T$ with decay $\lambda \in (0,1)$ is

$$
\mathrm{EMA}(T,\lambda) = \frac{1-\lambda}{1-\lambda^{T}}\sum_{t=1}^{T} \lambda^{t-1} P(t)
$$

Geometric weights on the same window, normalized to sum to one. $\lambda$ closer to 1 is slower. Recursive EMAs seeded on a sample that includes the future are look-ahead. Use SMA or EMA; do not mix them mid-history without documenting a switch.

Let $P$ be the price at $t=0$, the bar **after** the MA sample (so the average does not contain the fill). The signed gap from price to the local level is

$$
P - \mathrm{MA}(T)
$$

Price minus local mean. Positive: price above the average → long. Negative: below → short. The single-MA rule keeps only the **sign** of this gap. Sizing by the gap width is a different overlay. If $P$ is the same close that entered the SMA, delay-0: the gap uses the fill print.

The single-MA rule takes the **sign** of that gap as the position. You are holding “price above its local mean” until price crosses back. Dual MA ([`004-two-moving-averages.md`](004-two-moving-averages.md)) replaces $P$ with a shorter MA; this file uses $P$ itself.

That is the whole strategy. Everything below is the sign rule, equality handling, and delay.

### Worked intuition

Index at 4100, 200-day SMA at 4000: $P>\mathrm{MA}$ → long the index (dual-momentum risk-on). Later the index prints 3990 while the SMA is still 4005: cross below → flatten or short. A one-day spike to 4200 that is also used as today’s fill will lift both $P$ and a delay-0 SMA; delay-1 keeps that spike out of the average and trades the next open. Chop around 4000 will flip often — that is whipsaw, and costs dominate.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t)$ | split- and dividend-adjusted price; $t=1$ is the most recent bar in the MA sample |
| $P$ | price at $t=0$, the bar after the MA sample |
| $T$ | MA length |
| $\lambda$ | EMA decay, used only if MA type is EMA |
| $\mathrm{MA}(T)$ | SMA or EMA |
| $s \in \{-1,0,+1\}$ | position side |
| $Q$ | signed share holdings |

## 4. Mathematics

### 4.1 Sign rule

The long rule is

$$
P > \mathrm{MA}(T) \quad\Rightarrow\quad \text{long / cover}
$$

Price above the local level: go long or cover a short. Strict inequality. $P$ is the decision-bar price; $\mathrm{MA}$ is from a sample that ends before the fill under delay-1. If both use the same close, you are delay-0.

The short rule is

$$
P < \mathrm{MA}(T) \quad\Rightarrow\quad \text{short / sell}
$$

Price below the local level: sell a long or open a short. Long-only books flatten instead of shorting. Borrow is required for this branch. Mixing SMA in the long rule with EMA in the short rule is not this spec.

Equality $P=\mathrm{MA}(T)$ is flat or keep-previous; document the choice. Default: keep-previous after warmup, flat until the MA is defined.

Long-only, short-only, or two-way. Multi-name: independent signals. Near dollar-neutral only if the book happens to split — not by constraint.

### 4.2 Holding-period P&L

Per-name P&L from entry to exit, $Q<0$ on shorts:

$$
\mathrm{P\&L} = Q\bigl(P_{\mathrm{exit}} - P_{\mathrm{entry}}\bigr) - \mathrm{costs}
$$

Share P&L minus costs, one name at a time. No $\sum w_i=0$ to check. Adjusted $P$ (or an explicit dividend term) is required; unadjusted series also break the MA on ex-dates. If you do X = fill at the same close that entered the MA, the backtest lies by collecting the cross bar.

Report hit rate and average win/loss separately. MA systems are right-tail trend, not high hit-rate.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, adjusted daily OHLC. Unadjusted prices break MAs on splits. Keep delisted names until the delist date. This step exists so a 2-for-1 is not a death cross. Survivorship makes old trend overlays look too clean.
2. **MA type.** Choose SMA or EMA and length $T$. If EMA, fix $\lambda$. Switching type mid-sample without a flag is a different path of $s$.
3. **Warmup.** Require $T$ bars before the first signal. Until then, $s=0$. An SMA(200) on 40 bars is not an SMA(200). This step exists to forbid a short-window look-alike.
4. **Signal.** Compute $\mathrm{MA}(T)$ on the sample that ends before the fill (delay-1 default). Compare to $P$ at the decision bar. Delay-1 exists so the fill is not inside the average.
5. **Side.** Apply the two inequalities. On equality, use the documented rule. Equality handling must be stable; flipping $s$ on exact ties is a hidden churn source.
6. **Size.** Independent per name. Caller sets $Q$. Do not impose dollar-neutrality. Forcing neutrality would turn timers into a cross-section this file does not define.
7. **Blotter.** Round to lot size, emit intents. Do not route live orders. The spec stops at intents.
8. **Hold.** While price stays on the same side of the MA. Exiting because a slower MA “disagrees” is the triple-MA file.

## 6. Execution protocol

- Delay-1: decide at the close, trade the next open, so the fill is not inside the MA. If you do X = fill on the decision close, the backtest lies by trading the print that moved $P$ versus the average.
- The 200-day SMA on an index is the dual-momentum risk-off switch: long the index only when $P>\mathrm{SMA}(200)$. If you do X = compute that SMA on a window that includes the fill, the switch is delay-0.
- Borrow required for any short. Cap participation vs ADV if needed. If you do X = short names with no borrow tape, the two-way backtest lies.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted daily OHLC (close is enough for MA on price)
- ADV if you cap participation
- Borrow availability for shorts

Not used by this spec: book value, earnings, SUE, industry map, option IV.

No restatement peeking. Delisted names stay until the delist date.

If you do X = feed unadjusted closes, splits look like signals. If you do X = recompute historical EMAs after a later correction, restatement peeking moves old crosses. If you do X = take ADV from the hold, the cap looks ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $T$ | 50 | also in $\{20, 100, 200\}$ |
| MA type | SMA | EMA requires $\lambda$ |
| long-only | false | if true, suppress shorts |
| delay | 1 bar | delay-0 is research-only |
| equality | keep-previous | after warmup |

## 9. Agent implementation contract

Build a Python module `strategies.single_moving_average` with:

1. `ma(prices, T, ma_type) -> float` — sample ends before the fill under delay-1.
2. `side(price, ma) -> {-1,0,+1}` — equality $P=\mathrm{MA}$ is flat or keep-previous; document the choice.
3. `pnl(Q, P_entry, P_exit, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Whipsaw.** Price oscillating through the MA is the failure mode. If you do X = count crosses without costs, the backtest lies about the regime that trades most.
- **Look-ahead.** Using the fill bar inside the MA inflates the backtest. If you do X = delay-0 and label it delay-1, the backtest lies.
- **Single-name weakness.** Same caveat as dual MA: a trend overlay, not a high-Sharpe one-name factor. If you do X = pick the one ticker where 200-day worked, the backtest lies about a system.

## 11. Acceptance tests

- A price series above a flat MA is always long after warmup.
- Delay-1: the fill bar is not inside the MA sample. If including the fill close changes the delay-1 MA, the implementation looks ahead and the backtest lies.
- Equality handling matches the documented choice.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
