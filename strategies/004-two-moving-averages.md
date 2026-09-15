---
rank: 4
slug: two-moving-averages
title: "Two Moving Averages"
asset_class: "equities"
style: "single-name trend / technical"
horizon: "Daily bars. Holding from crossover to opposite crossover, optionally with a price stop."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 004. Two Moving Averages

| Field | Value |
|---|---|
| Popularity rank (this kit) | 4 of 101 |
| Why it sits here | The default dual-MA crossover (e.g. 10/30, 50/200). Most widely coded technical rule in equities, FX, and futures. |
| Aliases | dual moving average, MA crossover |
| Asset class | equities |
| Style | single-name trend / technical |
| Typical horizon | Daily bars. Holding from crossover to opposite crossover, optionally with a price stop. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Replace the raw price in the single-MA rule with a shorter MA. Long when the fast MA is above the slow MA; short when below. Optional stop-loss on the last close. Signals are independent per name. Single-name MAs are statistically weak; the same rule becomes a trend system when applied to a large futures or ETF book.

You are betting that a short-horizon local price level staying above a long-horizon local level is a continuation of drift, not a forecast of a target price. You hold the **sign** of fast minus slow until it flips or a stop hits. You are not ranking names against each other, not targeting dollar-neutrality, and not claiming a high hit-rate.

You are also not running the single-MA overlay ([`037-single-moving-average.md`](037-single-moving-average.md)), which compares *price* to one MA, or the triple-MA filter ([`038-three-moving-averages.md`](038-three-moving-averages.md)), which requires a stack to enter. Dual MA is the middle object: two levels, one sign.

Typical user: a CTA-style overlay on futures or ETFs, or a discretionary equity chartist automating a 10/30 or 50/200 rule. Horizon intuition: daily bars, hold from crossover to opposite crossover — often weeks to months in a trend, hours to days of churn in a range. If you put today’s close inside both MAs and fill on that same close, the backtest is an optimistic delay-0 research object, not a live book.

## 2. First principles

A moving average is a local estimate of the price level. Index bars so that $t=1$ is the most recent bar in the window and $t$ increases into the past. The simple moving average of length $T$ is the equal-weight level:

$$
\mathrm{SMA}(T) = \frac{1}{T}\sum_{t=1}^{T} P(t)
$$

Equal weight on the last $T$ adjusted closes (or on the window that ends before the fill under delay-1). This is a level, not a return. A split without adjustment drops $P$ by half and looks like a crash through the slow MA. The sum does not include a future bar; if $t=1$ is the fill bar, you have delay-0. That is why the default window ends at yesterday.

The exponential moving average of length $T$ with decay $\lambda \in (0,1)$ is the normalized geometric weight on the same window:

$$
\mathrm{EMA}(T,\lambda) = \frac{1-\lambda}{1-\lambda^{T}}\sum_{t=1}^{T} \lambda^{t-1} P(t)
$$

More weight on recent bars, still a finite window of length $T$, still normalized so the weights sum to one. $\lambda$ closer to 1 is slower. Use the same $\lambda$ and the same type on fast and slow; mixing SMA slow with EMA fast is a third rule. Recursive EMAs that seed from the whole sample including the future are look-ahead.

Write $\mathrm{MA}$ for either estimator. Let $T'<T$ be a shorter window. Then $\mathrm{MA}(T')$ is a short-horizon level and $\mathrm{MA}(T)$ is a long-horizon level. Their difference is a local-drift estimate:

$$
\mathrm{MA}(T') - \mathrm{MA}(T) \approx \text{recent level minus slow level}
$$

When the fast level is above the slow level, recent prices sit above the longer local mean: a positive local drift estimate. The dual-MA rule keeps only the **sign** of that difference, not its magnitude. You do not size bigger when the gap is wide unless the caller adds a separate vol rule. The approximation is spoken, not a new model: it is why people look at crossovers at all.

The dual-MA rule takes the **sign** of that difference as the position. You are not forecasting a target price. You are holding the sign of short-horizon level minus long-horizon level until it flips (or a stop hits).

That is the whole strategy. Everything below is the sign rule, the optional stop, and how not to use the fill bar inside the average.

### Worked intuition

Name X, already-adjusted closes. Slow SMA(30) sits at 100, fast SMA(10) sits at 103: fast above slow → long. Later the fast SMA rolls down through 100 while the slow is still 100: crossover down → sell the long (and short, unless long-only). A one-bar spike to 120 that is also used as today’s fill will yank the fast MA up and let you “buy the spike” in a delay-0 backtest; delay-1 keeps that spike out of both MAs and trades the next open instead. Sideways chop around 100 will cross the two averages every few days — that is whipsaw, and costs dominate.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t)$ | split- and dividend-adjusted price; $t=1$ is the most recent bar in the MA window |
| $T'$ | fast length, $T'<T$ |
| $T$ | slow length |
| $\lambda$ | EMA decay, used only if MA type is EMA |
| $\mathrm{MA}(\,\cdot\,)$ | SMA or EMA, same type on both legs |
| $\Delta$ | stop fraction (e.g. $0.02$) |
| $P_1$ | yesterday’s price, used only by the stop |
| $s \in \{-1,0,+1\}$ | position side (short / flat / long) |
| $Q$ | signed share holdings |

## 4. Mathematics

### 4.1 Crossover signal

Compute both averages on a window that **ends before** the fill. The long rule is

$$
\mathrm{MA}(T') > \mathrm{MA}(T) \quad\Rightarrow\quad \text{long / cover short}
$$

Fast above slow means the short-horizon level cleared the long-horizon level: go long, or cover an existing short. The inequality is strict. This is a state change, not a rank. If you compute the MAs on a window that includes the fill close, the inequality uses the same print you claim to trade — delay-0, research-only.

The short rule is

$$
\mathrm{MA}(T') < \mathrm{MA}(T) \quad\Rightarrow\quad \text{short / sell long}
$$

Fast below slow: sell a long, or open a short if two-way. Same delay rule as the long side. Long-only books suppress this branch; they flatten instead of shorting. Mixing SMA on one side of the inequality with EMA on the other is not this spec.

Equality $\mathrm{MA}(T')=\mathrm{MA}(T)$ is flat or keep-previous; document the choice. Default: keep-previous after warmup, flat until both MAs are defined.

### 4.2 Optional stop

After a long is on, flatten if the last close has broken yesterday’s price by $\Delta$:

$$
s=+1 \ \text{and}\ P < (1-\Delta) P_1 \quad\Rightarrow\quad \text{flatten}
$$

This is a price stop against yesterday’s close, not against the MA. It exists to cut a long that is already on when the tape gaps down through a fraction $\Delta$ (default 2%). It does not reverse to short unless a crossover also fires and you documented reverse-on-stop — default is flatten only. If no position exists, the stop does not fire; it is not an entry rule.

After a short is on, flatten if

$$
s=-1 \ \text{and}\ P > (1+\Delta) P_1 \quad\Rightarrow\quad \text{flatten}
$$

Symmetric squeeze stop on a short. $P_1$ is yesterday’s price, not the entry price and not the slow MA. Using the entry price instead is a different (and common) stop; this file uses $P_1$. Default $\Delta=0.02$. The stop fires only after a position exists.

$P_1$ is yesterday’s price. Default $\Delta=0.02$. The stop fires only after a position exists.

### 4.3 Book and P&L

Compute two MAs on each name independently. No cross-sectional interaction. The book can be long-only, short-only, or two-way. With many names it can be near dollar-neutral **by accident**, not by constraint.

Per-name P&L from entry to exit, $Q<0$ on shorts:

$$
\mathrm{P\&L} = Q\bigl(P_{\mathrm{exit}} - P_{\mathrm{entry}}\bigr) - \mathrm{costs}
$$

Share P&L plus costs, one name at a time. There is no $\sum_i w_i=0$ identity to check. Dividends belong in an adjusted $P$ series or as an explicit cash term; unadjusted prices will also break the MAs on ex-dates. If you do X = mark delay-0 fills at the same close that entered the MA, the backtest lies by collecting the bar that caused the crossover.

Report hit rate and average win/loss separately. MA systems are right-tail trend, not high hit-rate.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, adjusted daily OHLC. Unadjusted prices break MAs on splits. Keep delisted names until the delist date. This step exists so a 2-for-1 does not look like a death cross. Dropping names that later delist makes historical trend overlays look cleaner than they were.
2. **MA type.** Choose SMA or EMA. If EMA, fix $\lambda$. Use the same type for fast and slow. Mixing types is a different rule and must not be a silent default.
3. **Warmup.** Require $T$ bars before the first signal. Until then, $s=0$. This step exists because an SMA(30) on 5 bars is not an SMA(30). Trading during warmup is look-ahead on a shorter, undefined average.
4. **Signal.** At bar $t$, compute $\mathrm{MA}(T')$ and $\mathrm{MA}(T)$ from prices with timestamp $\le t$ if delay-0, or $\le t-1$ if delay-1 (default). Apply the two crossover inequalities. Delay-1 exists so the fill bar is not inside the average.
5. **Stop.** If a position is on, apply the $\Delta$ stop using $P_1$ = previous close. Stops flatten; they do not reverse unless a crossover also fires on the same bar — document that choice. Default: flatten only. The stop exists to cut gaps; it is not a second entry engine.
6. **Size.** Independent per name. Caller sets $Q$ (fixed shares, fixed dollars, or vol-scaled). Do not impose dollar-neutrality. Forcing $\sum w_i=0$ would turn a set of timers into a cross-sectional book this spec does not define.
7. **Blotter.** Round to lot size, emit intents. Do not route live orders. Intents, not live routing: the spec stops at the blotter.
8. **Hold.** From crossover to opposite crossover, or until the stop. Stretching a long after a death cross because “the slow MA is still rising” is the triple-MA file, not this one.

## 6. Execution protocol

- Decide at the close, trade the next open (delay-1) to avoid using the same close in the MA and the fill. If you do X = fill at the crossover close, the backtest lies by assuming you traded inside the print that moved the fast MA.
- Intrabar crossovers on the last print are delay-0 and optimistic. If you do X = use a running last-print MA as if it were a completed bar, the backtest lies about what a close-based rule would have done.
- Cap participation vs ADV if the name is small. Borrow required for any short. If you do X = short names with no borrow tape, the two-way backtest lies about the short side.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted daily OHLC (close is enough for SMA/EMA on price; highs/lows unused by this spec)
- ADV if you cap participation
- Borrow availability for shorts

Not used by this spec: book value, earnings, SUE, industry map, option IV.

No restatement peeking. Delisted names stay until the delist date.

If you do X = feed unadjusted closes, splits look like signals. If you do X = recompute historical EMAs after a later price correction, restatement peeking moves old crossovers. If you do X = take ADV from the holding window, the participation cap looks ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $T'$ | 10 | fast length |
| $T$ | 30 | slow length; also common: 50/200 |
| MA type | SMA | EMA requires $\lambda$ |
| $\Delta$ | 0.02 | stop off; set `None` to disable |
| long-only | false | if true, suppress shorts |
| delay | 1 bar | delay-0 is research-only |
| equality | keep-previous | after warmup |

## 9. Agent implementation contract

Build a Python module `strategies.two_moving_averages` with:

1. `sma(prices, T) -> float` and `ema(prices, T, lam) -> float` — window ends before the fill under delay-1.
2. `signal(prices, T_fast, T_slow, ma_type, delay) -> {-1,0,+1}` — explicit delay.
3. `apply_stop(side, P, P_1, Delta) -> {-1,0,+1}` — fires only if a position exists.
4. `pnl(Q, P_entry, P_exit, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Whipsaw.** Sideways markets cross the two MAs repeatedly; costs dominate. If you do X = count crossovers without costs, the backtest lies about the only regime where the rule trades a lot.
- **Look-ahead.** Using the same bar’s close in the MA and the fill inflates the backtest. If you do X = delay-0 and still report delay-1 Sharpes, the backtest lies.
- **Single-name weakness.** The rule is a trend overlay, not a high-Sharpe equity factor on one name. If you do X = pick the one ticker where 10/30 worked and hide the rest, the backtest lies about a system.

## 11. Acceptance tests

- A strictly increasing series must be long after both MAs are defined.
- A one-bar spike must not look ahead under delay-1: the fill bar is not inside the MA. If including the spike in the MA changes the delay-1 signal, the test must fail — that implementation looks ahead and the backtest lies.
- Stop fires only after a position exists. A stop that enters from flat is a different rule.
- Unadjusted split must **not** be used: a 2-for-1 split without adjustment must not flip the signal if adjusted prices would not.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
