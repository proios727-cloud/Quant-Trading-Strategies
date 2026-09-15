---
rank: 7
slug: futures-trend-following
title: "Futures Trend Following (Momentum)"
asset_class: "futures / commodities"
style: "time-series momentum / CTA"
horizon: "Formation $T$ in days/weeks/months; monthly or weekly rebalance"
instruments: "listed futures"
---

# 007. Futures Trend Following (Momentum)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 7 of 101 |
| Why it sits here | The core managed-futures / Moskowitz–Ooi–Pedersen TSMOM specification. Among the most widely allocated systematic styles. |
| Aliases | TSMOM, CTA trend, time-series momentum |
| Asset class | futures / commodities |
| Style | time-series momentum / CTA |
| Typical horizon | Formation $T$ in days/weeks/months; monthly or weekly rebalance |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Each futures market is its own timer. If the trailing excess return is positive, go long that contract; if negative, go short. Scale by inverse volatility so a noisy metal does not dominate a quiet rate future.

You are betting that the sign of a market’s own past excess return continues into the next holding period. That is time-series momentum, not a rank of winners versus losers. A copper uptrend and a bond downtrend can both be on at the same time; they do not compete for a decile slot.

You are not running the equity 12-1 skip-month sort (`001`). You are not forcing the book to be dollar-neutral unless the caller turns that overlay on. Neutrality is optional because the raw signal is allowed to be net long when most markets trend up. You are also not forecasting a level with an HP filter unless that causal filter is explicitly switched on; the default timer is the raw formation return.

Typical users are CTAs, risk-parity overlays that add a trend sleeve, and academic TSMOM replications. Instruments are listed futures after volume and open-interest filters: commodities, rates, equity indices, and FX futures. Horizon intuition: formation of 12 months is the textbook window; 1–3 month windows exist but chatter more. Rebalance monthly (weekly allowed). The hold is one rebalance period, not a multi-year discretionary view.

Crashes after long trends are the known left tail: the sign is still long into the break. Inverse-vol scaling does not hedge crisis correlation. Size from a window that has already ended, then delay-1 into the next session.

## 2. First principles

Let $R_i$ be the excess return of futures $i$ over a formation window that **ends before** the fill. Time-series momentum is the claim that the sign of that return is positively correlated with the next holding-period excess return:

$$
\mathbb{E}[R_{i,t+1}^{\mathrm{fwd}} \mid R_{i,t}] \approx \lambda\,\mathrm{sign}(R_{i,t}), \qquad \lambda>0
$$

The conditioning information is $R_{i,t}$ for that market alone. $\lambda>0$ is continuation of the sign, not a statement that last week’s tick continues. You are not ranking $i$ against $j$. You are asking, for each $i$ alone, whether its own past was up or down. That is the difference versus cross-sectional equity momentum. If you skip the “ends before the fill” clause and include the fill bar in $R_{i,t}$, the backtest lies: that bar was not known when you sized.

A mean-variance investor with diagonal covariance $C_{ij}=\sigma_i^2\delta_{ij}$ and expected excess $E_i=\eta_i\sigma_i$, where $\eta_i=\mathrm{sign}(R_i)$, holds

$$
w_i \propto C^{-1}E \propto \frac{\eta_i}{\sigma_i}
$$

So inverse-vol scaling is the MV book under a diagonal covariance, not an extra heuristic. The diagonal assumption is load-bearing and false in crises, when everything trends together; the formula still defines the *intended* weights, not the realized risk. Instability when $\lvert R_i\rvert$ is tiny is the same story: $\mathrm{sign}(0)$ is noise, so replace the raw sign with a squash or with $E_i=R_i$.

That is the whole strategy. Everything below is how to measure $R_i$, how to roll the contract, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | liquid futures after volume / open-interest filters |
| $P_i(t)$ | generic (or rolled) futures price used for returns |
| $R_i$ | formation excess return on $i$ |
| $\eta_i$ | $\mathrm{sign}(R_i)$, or a smooth substitute |
| $\sigma_i$ | realized vol of $i$ on a window that ends before the fill |
| $w_i$ | signed weight; $w_i>0$ long |
| $\gamma$ | scale mapping scores into weights |
| $\phi=P_1/P_2$ | front / second-month price ratio (backwardation if $\phi>1$) |
| $\kappa$ | squash scale for $\tanh(R_i/\kappa)$ |

Gross-one means $\sum_i \lvert w_i\rvert=1$. Dollar-neutral, if requested, adds $\sum_i w_i=0$.

## 4. Mathematics

### 4.1 Formation return

On a lookback that ends at $t_2$ before the fill, take the excess return of the rolled generic. Log or simple is interchangeable on monthly bars. Default window: $T=12$ months (TSMOM). Shorter 1–3 month windows are allowed.

The generic is a stitched price. Roll P&L belongs in the holding-period return, not in a hidden additive “roll alpha.” If the roll map uses $t+1$ open interest to decide a $t$ roll, the backtest lies.

Optional: replace raw prices by an EMA, HP, or Kalman level **fit only on data $\le t_2$**, then compute $R_i$ from that level. A two-sided filter on the full sample is look-ahead. If you do $X$ = run HP on the entire backtest then read $S^\ast_t$, every $t$ has seen the future, and the timer is not tradable.

### 4.2 Sign and weights

The raw timer is

$$
\eta_i = \mathrm{sign}(R_i)
$$

This is $+1$, $-1$, or, at exactly zero, a convention you must document (default: treat $0$ as flat, $\eta_i=0$). A raw sign on a 1-basis-point formation return is as loud as a sign on a 40% return. That is why the squash exists.

The diagonal-MV book is

$$
w_i = \gamma\,\frac{\eta_i}{\sigma_i}
$$

$\sigma_i$ is realized vol ending at $t_2$. Dividing by $\sigma_i$ equalizes risk contributions under the diagonal story. If $\sigma_i$ is computed through the fill bar, weights peek at the hold. Rebuild $\gamma$ after any name drop so the next identity holds.

with $\gamma$ chosen so

$$
\sum_i \lvert w_i\rvert = 1
$$

Gross-one is the budget. It is not dollar-neutrality. After ADV clips, rebuild $\gamma$ if the caller requires the identity to hold exactly; otherwise the residual sits in a margin buffer, not in a silent extra contract.

When $\lvert R_i\rvert$ is small, $\mathrm{sign}$ chatters. Two replacements, both legal in this spec:

$$
\eta_i = \tanh\bigl(R_i/\kappa\bigr)
$$

Tanh saturates large moves and shrinks near-zero moves, so a 2 bp wiggle does not flip a full-size position. Default $\kappa$ is the cross-sectional standard deviation of $R_i$ on the same date. A $\kappa$ estimated on the full sample, including future $R_i$, is look-ahead.

or set the MV mean to the return itself, $E_i=R_i$, which yields $w_i\propto R_i/\sigma_i^2$. Default $\kappa$ is the cross-sectional standard deviation of $R_i$. Pick one timer per run and document it. Mixing $\mathrm{sign}$ and $R_i/\sigma_i^2$ inside a date is two strategies.

### 4.3 Optional dollar-neutrality

The book above can be net long when most markets are in uptrends. To force $\sum_i w_i=0$, demean the inverse-vol scores:

$$
w_i = \gamma\left(\frac{\eta_i}{\sigma_i} - \frac{1}{N}\sum_j\frac{\eta_j}{\sigma_j}\right)
$$

Demeaning subtracts the cross-sectional mean of the inverse-vol scores so the weights sum to zero before $\gamma$ is rebuilt. It is an overlay, not a better estimate of $\lambda$. Then rebuild $\gamma$ so $\sum_i \lvert w_i\rvert=1$. Equivalently, split long and short cohorts $H_\pm$ with separate scales $\gamma_\pm$ so both $\sum w_i=0$ and $\sum \lvert w_i\rvert=1$ hold. To avoid a skewed sign count, replace $R_i$ by $R_i-R_m$ with $R_m=N^{-1}\sum_j R_j$ before taking $\eta_i$. If you demean after clipping, the identity can break; demean, then clip, then rebuild.

### 4.4 Holding-period P&L

Futures P&L is variation margin. There is no full-notional cash outlay. Let $R_i^{\mathrm{fwd}}$ be the excess return of the **traded** contract from fill to next rebalance, including roll P&L if the generic rolls inside the hold.

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

$D_i = I w_i$ is signed notional, not margin. If you divide P&L by margin instead of by $I$, Sharpe is not comparable to the rest of this kit. Costs include commissions, bid/ask on rolls, and any extra tick paid for a delayed fill. Report net return on gross $I$, Sharpe on non-overlapping holds, and

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

Turnover here is weight turnover, not contract-roll turnover. A roll that keeps $\eta_i$ unchanged still prints roll costs inside $R_i^{\mathrm{fwd}}$. Roll P&L is part of $R_i^{\mathrm{fwd}}$, not an extra alpha term. If you do $X$ = strip roll P&L out of $R^{\mathrm{fwd}}$ and call the rest “pure trend,” the backtest lies about what a listed book actually earned.

## 5. Step-by-step algorithm

1. **Universe.** Listed futures with a minimum ADV and open interest. Skip thin months. Keep delisted contracts until last trade date. This step exists so survivorship does not drop the markets that trended to zero or were delisted after a crash.
2. **Generic.** Build a rolled price series. The roll rule is independent of the signal (calendar or open-interest roll, chosen once). This step exists because the timer needs a continuous excess-return series; the roll rule must not peek at $t+1$ open interest to label a $t$ front month.
3. **Formation.** Compute $R_i$ on $[t_1,t_2]$ with $t_2<t_{\mathrm{fill}}$. Vol $\sigma_i$ on $T$ or on a separate window (default 60 days) that also ends at $t_2$. This step exists to keep the signal and the risk scaler causal. A vol that includes the hold shrinks weights on markets that already moved — look-ahead.
4. **Timer.** $\eta_i=\mathrm{sign}(R_i)$, or $\tanh$, or $E_i=R_i$. Drop names with missing $R_i$ or $\sigma_i$. This step exists because a missing vol is not zero vol; imputing it overweights the name.
5. **Size.** $w_i=\gamma\eta_i/\sigma_i$, then $\sum\lvert w_i\rvert=1$. Optional demean for dollar-neutrality. This step exists to turn signs into a budgeted book.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV (or of open interest). After clipping, rebuild $\gamma$ if the gross constraint is required to hold exactly. This step exists so a thin month cannot absorb the whole risk budget.
7. **Blotter.** Convert to contracts using the multiplier and the fill price. Round to whole contracts. Residual cash / margin buffer; never live routing. This step exists because futures trade in integer contracts; ignoring the multiplier misstates notional by orders of magnitude.
8. **Rebalance.** Monthly or weekly on a fixed calendar. Contract rolls fire on their own schedule even if the sign did not change. This step exists because a roll is a market event, not a signal event. Skipping a roll because $\eta_i$ is unchanged leaves you in a dead month.

## 6. Execution protocol

- Default fill: next session after $R_i$ is known. Delay-0 same-bar marks are research-only. If you do $X$ = mark and trade the same close that completed $R_i$, the backtest lies.
- Rolls are not signal events. Do not skip a roll because $\eta_i$ is unchanged.
- If a contract is limit-locked or halted, drop it and rebuild $\gamma$ on the remainder. Do not carry a stale sign through a halt. A locked limit is not a tradable fill at the last print.

## 7. Data contract

Required, point-in-time:

- Generic or contract-level futures prices, with the roll map dated $\le t_2$
- Volumes and open interest for filters and caps
- Contract multipliers, tick sizes, and first-notice / last-trade dates
- Term structure (front and deferred) if $\phi$ is used as a diagnostic
- Margin parameters for notional-to-margin translation (reporting only)

Not used by this spec: equity book value, earnings, FX fixing discounts. COT is optional and off by default.

No look-ahead on the roll: a roll decided with $t+1$ open interest is not a $t$ roll. If you do $X$ = choose the front month with tomorrow’s volume, the generic path was not tradable. If you do $X$ = use a back-adjusted series that shifts the entire history by a future roll, formation returns at $t_2$ have seen later rolls.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation $T$ | 12 months | TSMOM; 1–3 months allowed |
| vol lookback | 60 days | ends at $t_2$ |
| $\kappa$ | xs std of $R_i$ | tanh squash |
| dollar-neutral | off | demean or split $H_\pm$ if on |
| rebalance | monthly | weekly allowed |
| price filter | off | EMA / HP / Kalman, causal only |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.futures_trend_following` with:

1. `formation_return(prices, t1, t2) -> pd.Series` — $R_i$, no look-ahead.
2. `weights(R, sigma, I, neutral=False, squash=None) -> pd.Series` — $w_i$ with $\sum\lvert w_i\rvert=1$ to `1e-8`; if `neutral`, also $\sum w_i=0$.
3. `blotter(weights, contract_price, multiplier, I) -> list[OrderIntent]` — whole contracts, never live routing.
4. `pnl(D, forward_excess, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$, roll included in $R^{\mathrm{fwd}}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Momentum crashes.** Sharp reversals after long trends; the sign is still long (short) into the break.
- **Diagonal covariance.** Crisis correlation makes the book much riskier than $\sum w_i^2\sigma_i^2$. Inverse-vol is not a hedge overlay.
- **Sign chatter.** Near-zero $R_i$ without squash flips every rebalance and pays two spreads for noise.
- **Roll / liquidity.** Thin deferred months around the roll can dominate costs. Holding into first notice is a different trade than the liquid generic.

## 11. Acceptance tests

- One name, $R>0$ → $w>0$; $R<0$ → $w<0$; $\lvert w\rvert=1$.
- Two names, equal $\sigma$, opposite signs → equal-magnitude opposite weights when `neutral=True`, $\sum w_i=0$, $\sum\lvert w_i\rvert=1$.
- Permuting prices after $t_2$ must not change $R_i$ or $w_i$ computed at $t_2$.
- A roll that changes the generic mid but not the sign still appears in $R^{\mathrm{fwd}}$ and in P&L.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
