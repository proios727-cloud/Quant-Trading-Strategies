---
rank: 81
slug: etf-mean-reversion-ibs
title: "ETF Mean-Reversion (Internal Bar Strength)"
asset_class: "ETFs"
style: "cross-sectional overnight mean-reversion"
horizon: "1-day hold typical"
instruments: "listed ETFs (equity sector, country, or index)"
---

# 081. ETF Mean-Reversion (Internal Bar Strength)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 81 of 101 |
| Why it sits here | IBS close-location-in-range is a popular short-horizon ETF / equity mean-reversion score (Pagonidis and others). |
| Aliases | internal bar strength, close location value |
| Asset class | ETFs |
| Style | cross-sectional overnight mean-reversion |
| Typical horizon | 1-day hold typical |
| Instruments | listed ETFs (equity sector, country, or index) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

ETFs that closed near the high of day look rich; near the low look cheap. Fade the cross-section next session: short high IBS, long low IBS, dollar-neutral.

You are betting that the close’s place in that day’s own range mean-reverts into the next session: a close at the high tends to give back, a close at the low tends to bounce, *relative to peers*. The book is a one-day residual reversal, not a market timer. High IBS names are short, low IBS names are long, net zero.

You are not ranking 12-month momentum. You are not fading a multi-day return. You are not an HFT file: decide after the cash close, trade next open, even if a live desk would try the close. You are not filling IBS with $1/2$ when $P_H=P_L$; that bar is undefined (halt or one-tick) and is dropped. A cluster-wide trend day makes most IBS prints high together; fading them loses. That is the known failure mode, not a reason to add a trend overlay in this file.

Typical users are short-horizon ETF mean-reversion sleeves. Horizon is one day. Turnover is near 1 daily. Overnight gaps can skip the reversion you scored at the close. Delay: next open, not same-close.

## 2. First principles

Let $P_H,P_L,P_C$ be the session high, low, and close. Internal bar strength is the close’s location in the day’s range:

$$
\mathrm{IBS} = \frac{P_C-P_L}{P_H-P_L}\in[0,1]
$$

This uses only that session’s H/L/C. $\mathrm{IBS}=1$ means the close **is** the high (the bar finished at the rich extreme). $\mathrm{IBS}=0$ means the close is the low. The denominator is the day’s range; if it is zero the score does not exist. Split-adjust H/L/C with the same factor or the ratio is garbage around corporate actions.

$\mathrm{IBS}=1$ means the close **is** the high (the bar finished at the rich extreme). $\mathrm{IBS}=0$ means the close is the low. Mean-reversion says a close at an extreme of the session’s own range tends to reverse into the next session:

$$
\mathbb{E}[R_{i,t+1}\mid \mathrm{IBS}_{i,t}] \approx -\lambda\bigl(\mathrm{IBS}_{i,t}-\tfrac12\bigr), \qquad \lambda>0
$$

The minus sign is the fade: high IBS, negative expected next return. $\lambda>0$ is the reversion strength, not a calibrated trading size. The centred score $Y=\mathrm{IBS}-1/2$ is positive for rich closes and negative for cheap ones. The trade is the cross-sectional fade: short high $Y$, long low $Y$, so the book is not a market timer. A cluster-wide trend day makes most IBS prints high together; fading them loses. That is the known failure mode, not a reason to add a trend overlay in this file.

That is the whole strategy. Everything below is the skip rule when $P_H=P_L$, the sort, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P_H,P_L,P_C$ | session high, low, close of ETF $i$ on day $t$ |
| $\mathrm{IBS}_i$ | internal bar strength on day $t$ |
| $Y_i=\mathrm{IBS}_i-1/2$ | centred score |
| $Q_H,Q_L$ | top and bottom IBS deciles |
| $w_i$ | signed weight; $w_i<0$ short high IBS |
| $\sigma_i$ | optional vol for $1/\sigma$ weights |
| $I$ | gross dollars |

Dollar-neutral: $\sum_i w_i=0$, $\sum_i \lvert w_i\rvert=1$.

## 4. Mathematics

### 4.1 IBS

On day $t$, using that day’s H/L/C only:

$$
\mathrm{IBS}_i = \frac{P_{C,i}-P_{L,i}}{P_{H,i}-P_{L,i}}
$$

Skip bars with $P_H=P_L$ (undefined IBS, typically a halt or a one-tick name). Do not set IBS to $1/2$ unless the caller explicitly wants a flat fill; default is drop. A stale print that fakes a high or low parks IBS at 0 or 1 by accident; liquidity screens exist for that.

Centred score:

$$
Y_i = \mathrm{IBS}_i - \tfrac12
$$

Positive $Y$ is rich (closed near the high), negative $Y$ is cheap. Sorting on IBS or on $Y$ is the same order. The centering is for intuition and for the $\lambda$ display above, not a second signal.

### 4.2 Cross-sectional fade

Sort the universe on IBS (equivalently on $Y$). Dollar-neutral: short the top decile, long the bottom decile. Uniform weights within legs, or $\propto 1/\sigma_i$ with $\sigma$ from a 20-day lookback ending at $t$.

Sign rule:

- high IBS ($Y>0$, closed near the high) → **short**
- low IBS ($Y<0$, closed near the low) → **long**

Do not invert this. A momentum overlay that buys high IBS is a different spec. $\sigma$ ending at $t$ is allowed because it does not include day $t+1$. Including $t+1$ vol in the weights peeks at the hold.

### 4.3 Holding-period P&L

Apply the score at the close of day $t$. Hold through day $t+1$ close, or next open → next close. Default for research: decide after the cash close, trade next open, exit next close (or next rebalance close).

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$R_i^{\mathrm{fwd}}$ is the simple return over that hold, including dividends if any. Overnight gaps are in $R^{\mathrm{fwd}}$, not a separate term. Same-close fill (trade the close you scored) is research-only: that close was not available as a fill after you saw H/L/C. Report one-day Sharpe on non-overlapping days and turnover (typically near $1$ because the book is rebuilt daily).

## 5. Step-by-step algorithm

1. **Universe.** Liquid ETFs, ADV minimum, borrow available for names that can be short. This step exists because a one-day fade on a thin ETF is all spread and a fake $P_H$.
2. **Bar.** Day-$t$ H/L/C with timestamp $\le t_{\mathrm{close}} < t_{\mathrm{fill}}$. This step exists so the score cannot see the next open, let alone the next close.
3. **IBS.** Compute $\mathrm{IBS}_i$. Drop $P_H=P_L$ and missing bars. This step exists because a zero range is undefined, not “neutral.”
4. **Sort.** Deciles on IBS. Short $Q_H$, long $Q_L$. This step exists to make the fade cross-sectional rather than a market timer on average IBS.
5. **Weights.** Uniform or $1/\sigma_i$ (20-day vol). $\sum w=0$, $\sum\lvert w\rvert=1$. This step exists to enforce dollar-neutrality after drops.
6. **Caps.** ADV clip. Rebuild if a short has no locate. This step exists so a missing locate does not leave a residual-long “cheap close” book.
7. **Blotter.** Next-open intents (default). Never live routing. This step exists because this is not an HFT close-cross.
8. **Hold.** One day. Flatten at the exit close; do not carry a stale IBS. This step exists because yesterday’s close location is not today’s signal.

## 6. Execution protocol

- Intraday live: still decide only with information strictly before the fill. This is not an HFT file. If you do $X$ = fill at the same close that produced H/L/C, the backtest lies.
- Liquidity screen on ADV. Wide-range ETFs with stale prints can fake a $P_H$ or $P_L$.
- If the next open is a halt, drop the name; do not use the previous close as a fill.

## 7. Data contract

Required, point-in-time:

- Daily (or session) high, low, close — unadjusted H/L must be treated carefully around splits; use split-adjusted H/L/C consistently
- ADV
- Borrow for shorts
- Official session times so “close” is the cash close, not a late print

Not used by this spec: book value, factors, NAV, formation returns over weeks.

If you do $X$ = use a late print as $P_C$ after the cash close, IBS was not the live close location. If you do $X$ = mix unadjusted highs with adjusted closes around a split, IBS can fall outside $[0,1]$ or explode. If you do $X$ = permute day $t+1$ bars into day $t$ H/L, the score looked ahead. Official session high/low; no restatement of the bar after $t$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| hold | 1 day | next open → next close |
| sort | deciles | |
| weights | equal | or $1/\sigma_i$ |
| vol lookback | 20 days | if used |
| $P_H=P_L$ | drop | do not fill $1/2$ |
| delay | next open | same-close fill is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.etf_mean_reversion_ibs` with:

1. `ibs(high, low, close) -> pd.Series` — $\mathrm{IBS}\in[0,1]$, `NaN` if $P_H=P_L$.
2. `weights(ibs, mode="dollar_neutral", sigma=None) -> pd.Series` — short high IBS, long low IBS, $\sum w=0$, $\sum\lvert w\rvert=1$ to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Trend days.** Fading high IBS into a continuation session loses. Most names print high IBS together; the cross-section does not save you.
- **Overnight gaps.** The open is not the close; $R^{\mathrm{fwd}}$ can skip the mean-reversion.
- **Stale prints.** A bad high or low places IBS at $0$ or $1$ by accident.
- **Short-leg failure.** Missing locates leave a residual-long “cheap close” book.

## 11. Acceptance tests

- $P_C=P_H>P_L$ → $\mathrm{IBS}=1$; $P_C=P_L<P_H$ → $\mathrm{IBS}=0$.
- Two names, IBS $1$ and $0$ → equal-dollar short and long, $\sum w=0$, $\sum\lvert w\rvert=1$.
- $P_H=P_L$ → name absent from weights, not IBS $=1/2$.
- Permuting day-$t+1$ bars must not change day-$t$ IBS or $w_t$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
