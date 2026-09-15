---
rank: 52
slug: fx-moving-averages-hp-filter
title: "FX Moving Averages with HP Filter"
asset_class: "foreign exchange"
style: "trend / filtered dual moving average"
horizon: "Monthly signals on several years of history; trades can be held weeks to months"
instruments: "FX spot; FX forwards (typically 1m); G10 and liquid EM pairs"
---

# 052. FX Moving Averages with HP Filter

| Field | Value |
|---|---|
| Popularity rank (this kit) | 52 of 101 |
| Why it sits here | Dual MA crossover is the workhorse CTA FX overlay; HP (Hodrick–Prescott / Whittaker–Henderson) pre-smoothing is the noise control for noisy FX spots. |
| Aliases | HP-filtered dual MA, Whittaker–Henderson FX trend |
| Asset class | foreign exchange |
| Style | trend / filtered dual moving average |
| Typical horizon | Monthly signals on several years of history; trades can be held weeks to months |
| Instruments | FX spot; FX forwards (typically 1m); G10 and liquid EM pairs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

FX spots are noisy. Filter out the high-frequency component, then apply two moving averages on the smooth trend $S^\ast(t)$. Buy when the fast average of $S^\ast$ is above the slow average; sell when it is below.

You are betting that the slow component of spot trends: after the high-frequency wiggle is stripped, a fast MA above a slow MA predicts a positive next holding-period FX excess return (long foreign), and the reverse predicts negative. The HP step is the noise control. It is not optional decoration.

You are not trading carry. $D$ is not in the signal; a combined book lives in `087`. You are not running a two-sided HP on the full sample. That leaks future spots into $S^\ast_t$ and is the most common way this file’s backtest lies. You are not claiming the dual MA works on raw $S$ the same way; the HP exists because raw FX chatter flips a 3/12 MA too often.

Typical users are CTA FX overlays and academic trend replications that want a smoother timer than raw TSMOM. Horizon intuition: monthly spots, $\ge 5$ years of history to fit HP, 3-month versus 12-month MAs on $S^\ast$, delay-1 into the next month’s first fixing. Ranging FX still chops, even on $S^\ast$. $\lambda$ too large freezes the trend into a straight line that never crosses.

## 2. First principles

Write spot as a slow trend plus a transitory shock:

$$
S(t) = S^\ast(t) + \nu(t)
$$

$S^\ast$ is the piece you are willing to trend-follow. $\nu$ is the high-frequency wiggle that makes a raw dual MA chatter. This split is an accounting identity once you pick a filter; it is not a claim that $\nu$ is white noise. A filter that uses $S(t+k)$ to form $S^\ast(t)$ puts future $\nu$ into today’s trend. Hodrick–Prescott / Whittaker–Henderson picks $S^\ast$ by penalizing both the fit residual and the second difference (curvature) of the trend.

Time-series trend on the smooth series is the usual dual-MA claim: if the short average of $S^\ast$ sits above the long average, the next holding-period FX excess return is more often positive than negative. Carry is **not** in this signal; a combined book lives in `087`.

That is the whole strategy. Everything below is the causal HP, the two averages, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S(t)$ | spot, domestic per 1 foreign |
| $S^\ast(t)$ | HP trend |
| $\nu(t)$ | residual $S-S^\ast$ |
| $\lambda$ | HP smoothness penalty |
| $n$ | observations per year (monthly $\Rightarrow n=12$) |
| $T_1<T_2$ | fast and slow MA lengths on $S^\ast$ |
| $\mathrm{MA}(T)$ | moving average of $S^\ast$ of length $T$ |
| $w$ | signed weight on the pair; $w>0$ long foreign |
| $F(t,T)$ | forward used to enter, if the blotter is forwards rather than spot |

## 4. Mathematics

### 4.1 HP objective

On a trailing window of length $T$ that **ends at the decision bar**,

$$
g = \sum_{t=1}^{T}\bigl[S(t)-S^\ast(t)\bigr]^2 + \lambda\sum_{t=2}^{T-1}\bigl[S^\ast(t+1)-2S^\ast(t)+S^\ast(t-1)\bigr]^2
$$

The first sum is the fit: $S^\ast$ should track $S$. The second sum is the smoothness penalty on curvature. $\lambda$ large means a nearly linear trend; $\lambda$ small means $S^\ast$ hugs $S$ and you have not filtered anything. The window must end at the decision bar. Running this $g$ on $t=1,\ldots,T_{\mathrm{full}}$ and then reading $S^\ast$ in the middle of the sample uses future $S$.

Choose the path $\{S^\ast(t)\}$ to minimise that criterion:

$$
\{S^\ast(t)\} = \arg\min g
$$

This is a linear smoother. The last point $S^\ast(T)$ on an expanding window is a function of $\{S(s):s\le T\}$ only if the window itself ends at $T$. A two-sided implementation that also uses $S(T+k)$ is look-ahead even if $\lambda$ is the default.

Heuristic penalty:

$$
\lambda = 100 n^2
$$

This is the usual annualization heuristic, not a likelihood estimate. Monthly data have $n=12$, so $\lambda=14400$. Estimation span $\ge 5$ years of monthly spots. Daily data need a different $n$; do not reuse 14400 on daily bars without changing $n$.

A two-sided HP run on $t=1,\ldots,T_{\mathrm{full}}$ uses $S(t+k)$ to form $S^\ast(t)$. That is look-ahead. The implementation must be expanding or one-sided: $S^\ast(t)$ is a function of $\{S(s):s\le t\}$ only. If you do $X$ = call a library `hpfilter` on the full series then back out a “live” signal, the backtest lies. The acceptance test that permutes $S(s)$ for $s>t$ exists specifically for this.

### 4.2 Dual MA on the trend

On $S^\ast$, compute $\mathrm{MA}(T_1)$ and $\mathrm{MA}(T_2)$ with $T_1<T_2$ (default $3$ and $12$ months).

Buy (long foreign) if the fast average is above the slow:

$$
\mathrm{MA}(T_1) > \mathrm{MA}(T_2) \;\Rightarrow\; w = +1
$$

Fast above slow is the uptrend timer on the *filtered* series. The MAs are themselves causal: they use $S^\ast(s)$ for $s\le t$ only. If $S^\ast$ already leaked, the MA cannot save you.

Sell (short foreign) if the fast average is below the slow:

$$
\mathrm{MA}(T_1) < \mathrm{MA}(T_2) \;\Rightarrow\; w = -1
$$

The downtrend is a short foreign / long domestic position, not a flat. Equal averages: flat. One signal per pair. Optional book: equal-weight or vol-target the signed positions across pairs, then $\sum\lvert w_i\rvert=1$. A panel mix does not change the look-ahead rule on each pair’s $S^\ast$.

### 4.3 Holding-period P&L

Enter via spot-plus-swap or via the 1m forward. Domestic P&L on a long foreign notional $N_{\mathrm{fx}}$ held from $t$ to $t+1$ is

$$
\mathrm{P\&L} = N_{\mathrm{fx}}\bigl(S(t+1)-S(t)\bigr) + \text{carry} - \mathrm{costs}
$$

Spot increment is the trend P&L. Carry still accrues if you hold FX balances even though $D$ is not the signal; include it in the identity so a long high-yield name is not credited only for $\Delta S$. Forwards settle on $S(t+T)-F(t,T)$ instead of $S(t+1)-S(t)$ plus explicit carry. Report Sharpe on non-overlapping holds and turnover of the signed $w$. If you omit carry in a high-rate pair, you are not marking the actual instrument.

## 5. Step-by-step algorithm

1. **Universe.** G10, optionally liquid EM. One signal per pair vs the numeraire, or a panel of crosses. This step exists so pegs and illiquid crosses do not get a dual-MA that cannot be filled.
2. **Sample.** Trailing monthly spots, span $\ge 5$ years, ending at month $t-1$ for a delay-1 book. This step exists because HP on a two-year window is an under-identified smoother, and because the last point must not be the fill month.
3. **HP.** Fit $S^\ast$ with $\lambda=100 n^2$ on that window only. Store only the last $S^\ast$ (or a one-sided recursion). Do not peek at month $t$’s close to trade month $t$’s close. This step exists to kill two-sided look-ahead.
4. **MAs.** $\mathrm{MA}(T_1)$ and $\mathrm{MA}(T_2)$ on the causal $S^\ast$ series. This step exists to turn a smooth level into a timer. MAs on raw $S$ are a different spec.
5. **Sign.** $+1$, $-1$, or $0$ as in §4.2. This step exists to map the crossover to a position; equality is flat, not last-sign.
6. **Book.** Optional: equal-weight or vol-target across pairs; skip thin forwards. This step exists so a single EM pair does not become the whole overlay.
7. **Blotter.** Spot or forward intents. Never live routing. This step exists because the spec is research.
8. **Rebalance.** Monthly after the new $S^\ast$ point is known. This step exists so you do not hold last month’s sign through a new $S^\ast$ without updating.

## 6. Execution protocol

- Default fill: next month’s first fixing after the month-end $S^\ast$ is known. If you do $X$ = use month $t$ close in $S^\ast(t)$ and fill that same close, the backtest lies.
- $\lambda$ is a parameter. Default $\lambda=100 n^2$ with $n=12$ for monthly data.
- If HP is implemented with a two-sided smoother in a library, wrap it so the $t$ output cannot see $s>t$. An acceptance test below exists specifically for this.

## 7. Data contract

Required, point-in-time:

- Monthly (or daily, then subsampled) spot mids, bid/ask
- Forwards if the blotter enters with $F(t,T)$
- Calendar / holiday gaps so month-end is a real fixing

Not used by this spec: equity fundamentals, the carry discount $D$ as a **signal** (P&L may still include carry).

If you do $X$ = run two-sided HP on the full backtest, $S^\ast(t)$ saw the future. If you do $X$ = splice a revised WM history into past months, the trend at $t$ was not the live trend. If you do $X$ = fit $\lambda$ by maximizing in-sample Sharpe of the dual MA, $\lambda$ peeked at the hold. Freeze the spot series as of the decision; no restatement of past fixings.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $T_1,T_2$ | 3, 12 months | fast / slow |
| $\lambda$ | $14400$ | $100 n^2$ with $n=12$ |
| HP span | $\ge 5$ years | monthly |
| weighting | one pair, $\lvert w\rvert=1$ | or equal / vol-target panel |
| delay | 1 month | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.fx_moving_averages_hp_filter` with:

1. `hp_trend(spot, lam, t) -> pd.Series` — $S^\ast(s)$ for $s\le t$ only; permuting $s>t$ must not change $S^\ast(t)$.
2. `signal(S_star, T1, T2) -> int` — $+1$, $-1$, or $0$.
3. `weights(signals, vols=None) -> pd.Series` — panel mix with $\sum\lvert w_i\rvert=1$ to `1e-8` if $N>1$.
4. `blotter(weights, instrument, I) -> list[OrderIntent]` — never live routing.
5. `pnl(N, spot_path, carry, costs) -> float` — matches the identity in §4.3.

Expose $\lambda$ as a parameter. Default $\lambda=100 n^2$ with $n=12$ for monthly data.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Look-ahead HP.** Two-sided full-sample filters invent a trend that was not tradable. This is the failure mode that makes paper Sharpes look like a different strategy.
- **Whipsaw.** Ranging FX still chops a dual MA, even on $S^\ast$.
- **$\lambda$ too large.** The trend becomes a straight line; the MA never crosses.
- **Carry crash while long high-beta EM.** This overlay does not know about $D$. A trend-long EM name still has crash risk.

## 11. Acceptance tests

- Permuting $S(s)$ for $s>t$ must not change $S^\ast(t)$ or the MA sign at $t$.
- $\mathrm{MA}(T_1)>\mathrm{MA}(T_2)$ → $w>0$; reverse → $w<0$.
- $\lambda=100\cdot 12^2=14400$ is the monthly default actually passed into `hp_trend`.
- Adding linear costs $\tau$ weakly decreases P&L.
- A constant $S(t)$ path yields $S^\ast=S$ and a flat dual-MA (no trade).

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
