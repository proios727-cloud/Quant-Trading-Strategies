---
rank: 56
slug: futures-mean-reversion
title: "Futures Contrarian Trading (Mean-Reversion)"
asset_class: "futures / commodities"
style: "cross-sectional reversal vs an equal-weight futures index"
horizon: "Weekly rebalance"
instruments: "listed futures"
---

# 056. Futures Contrarian Trading (Mean-Reversion)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 56 of 101 |
| Why it sits here | Weekly loser/winner fade in futures, analog of equity short-term reversal. |
| Aliases | futures reversal, cross-sectional fade |
| Asset class | futures / commodities |
| Style | cross-sectional reversal vs an equal-weight futures index |
| Typical horizon | Weekly rebalance |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Buy futures that underperformed an equal-weight “market” of the universe, sell outperformers. Residuals sum to zero, so a linear fade is automatically dollar-neutral. Optional volume and open-interest screens keep the book in names that actually traded.

This is the futures analogue of single-cluster equity reversal, with the cluster equal to the whole futures universe. You are not betting that commodities go up. You are betting that last week’s relative winners and losers swap. File 007 is the opposite sign (trend). File 054 sorts on curve shape, not on last week’s residual.

Typical users are short-horizon futures sleeves that can trade weekly. Delay-1: this week’s residual trades next week’s close (or next Monday). Friday close-to-close with no delay is research-only. Mixing crude with FX futures creates a fake “market” $R_m$; keep the universe coherent or the residual is a sector bet.

## 2. First principles

Write each contract’s formation excess return as a common piece plus an idiosyncratic shock:

$$
R_i = R_m + \varepsilon_i
$$

The split is an accounting identity once $R_m$ is defined as the equal-weight mean, not a CAPM claim. If the universe is “all liquid futures,” $R_m$ is a mixed-asset factor. If the universe is grains only, $R_m$ is a grain factor. Choose that on purpose.

The equal-weight futures “market” is the sample estimate of the common piece:

$$
R_m = \frac{1}{N}\sum_{i=1}^N R_i
$$

Dropping missing $R_i$ without rebuilding $N$ will bias $R_m$. Value-weighting $R_m$ by open interest is a different market and a different residual. The residual $R_i-R_m$ sums to zero. Mean-reversion says a large relative shock tends to fade over the next week, so the position is proportional to $-(R_i-R_m)$.

That is the whole strategy. Everything below is the scale $\gamma$, optional vol suppression, the activity filter, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | futures after liquidity and delivery filters |
| $R_i$ | formation excess return (default: last week) |
| $R_m$ | equal-weight mean of $R_i$ |
| $w_i$ | signed weights |
| $\gamma$ | scale mapping residuals into weights |
| $\sigma_i$ | trailing vol for optional suppression |
| $V_i, V_i'$ | this week and prior week volume |
| $U_i, U_i'$ | this week and prior week open interest |
| $v_i=\ln(V_i/V_i')$ | volume activity |
| $u_i=\ln(U_i/U_i')$ | open-interest activity |
| $I$ | gross notional |
| $D_i=w_i I$ | signed notional |

## 4. Mathematics

### 4.1 Market residual

Formation window ends before the fill. Default: last week’s excess returns.

$$
R_m = \frac{1}{N}\sum_i R_i
$$

$R_m$ uses only names that will be eligible for $w_i$. Computing $R_m$ on the full universe then applying the activity filter later puts excluded names into the market and not into the book, which breaks $\sum(R_i-R_m)=0$ on survivors.

Linear fade with gross-one constraint:

$$
w_i = -\gamma (R_i - R_m)
$$

The minus sign is the whole strategy: last week’s winner is short. Choose $\gamma>0$ so that

$$
\sum_i \lvert w_i\rvert=1
$$

Then $\sum_i w_i=0$ automatically because $\sum_i(R_i-R_m)=0$. If after clipping that automatic neutrality is lost, restore it; do not keep only the longs. Sign: last week’s winner ($R_i>R_m$) is short; last week’s loser is long.

### 4.2 Vol suppression

Optional, applied **before** renormalizing $\gamma$: replace $R_i-R_m$ with $(R_i-R_m)/\sigma_i$ or $(R_i-R_m)/\sigma_i^2$ so high-vol names do not dominate. $\sigma_i$ from a 20–60 day window ending at $t$. Using next week’s realized vol to scale this week’s residual is look-ahead. Suppression is not a second alpha; it is a risk budget.

### 4.3 Activity filter

Optional two-week screen. Volume and open-interest activity:

$$
v_i=\ln(V_i/V_i'), \qquad u_i=\ln(U_i/U_i')
$$

Keep the upper half by $v_i$, then the **lower** half of those by $u_i$, then apply the same $w_i$ on the survivors and rebuild $R_m$ and $\gamma$. Interpretation: names that traded more this week, but without a matching jump in open interest. Rebuild $R_m$ on survivors so neutrality still holds. A name in the lower half of $v_i$ is absent from $w$, not zero-weighted inside the old $R_m$.

### 4.4 Holding-period P&L

Weekly variation margin minus costs:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Report return on $I$, Sharpe on **non-overlapping** weeks, and turnover $\frac12\sum_i\lvert w_{i,t}-w_{i,t-1}\rvert$. $R_i^{\mathrm{fwd}}$ is next week’s excess return of the contract you hold, including any roll. Using this week’s $R_i$ as if it were the holding return is look-ahead.

## 5. Step-by-step algorithm

1. **Universe.** Listed futures (commodities, and optionally other liquid futures). Skip delivery months. This step defines $R_m$. A mixed crude-and-FX universe is a choice you must document, not a default.
2. **Formation.** Last-week excess returns from stamps $\le t < t_{\mathrm{fill}}$. Drop missing $R_i$; rebuild $N$. Including the fill week in $R_i$ uses the holding return as the signal.
3. **Filter (optional).** Apply $v_i$, then $u_i$, as in 4.3; recompute $R_m$ on survivors. Skipping the rebuild is the usual neutrality bug.
4. **Residual.** $R_i-R_m$. Optional divide by $\sigma_i$ or $\sigma_i^2$. $\sigma_i$ ends at $t$.
5. **Size.** $w_i=-\gamma(R_i-R_m)$ with $\sum\lvert w_i\rvert=1$. The minus sign must survive any vol scaling.
6. **Caps.** Clip by ADV / open interest; restore $\sum w_i=0$ after clipping. Thin ags will otherwise dominate.
7. **Blotter.** Contracts from $D_i=w_i I$, round, emit intents. Do not route live orders. If a contract cannot be shorted, drop it and rebuild $R_m$ and $\gamma$; do not keep only the longs.
8. **Rebalance.** Weekly. Delay-1: this week’s residual trades next week’s close (or next Monday). Same-Friday fills are research-only.

## 6. Execution protocol

- Default fill: next close after the weekly residual is known. Delay-0 Friday close-to-close is research-only.
- Skip delivery months. Roll before first notice.
- If a contract cannot be shorted (rare in listed futures, but possible via position limits), drop it and rebuild $R_m$ and $\gamma$. Do not keep only the longs.

## 7. Data contract

Required, point-in-time:

- Generic or contract-level futures prices on the formation and holding weeks
- Volume and open interest if the activity filter is on
- Delivery / first-notice calendar

Not used by this spec: COT hedging pressure, front/second $\phi$ as the signal, 5-year spot value, equity book value, earnings, SUE.

No look-ahead on next week’s returns when forming $w_t$. A generic series that uses next week’s roll date to pick this week’s contract is leak.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| formation | 1-week returns | |
| vol lookback | 20–60 days | if suppression on |
| vol suppress | off | $1/\sigma_i$ or $1/\sigma_i^2$ |
| activity filter | off | $v_i$ then $u_i$ |
| rebalance | weekly | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.futures_mean_reversion` with:

1. `residuals(returns) -> pd.Series` — $R_i-R_m$, no look-ahead.
2. `activity_filter(V, Vp, U, Up) -> pd.Index` — survivors from $v_i$, $u_i$.
3. `weights(residuals, I, vol=None) -> pd.Series` — $\sum w_i=0$, $\sum\lvert w_i\rvert=1$ to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — contracts, never live routing.
5. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Trends persist.** A strong drift week makes residuals keep going; the fade loses. That is why this file is not file 007: the sign is the opposite, and both can be wrong in the same week.
- **Thin ags.** Capacity and gaps in agricultural contracts. ADV caps exist because of limit moves, not because of politeness.
- **Wrong universe.** Mixing crude with FX futures creates a fake “market” $R_m$. The residual then is “oil versus the dollar,” which you did not size as FX.
- **Delivery.** Holding into delivery is not this spec.
- **Filter leakage.** Computing $R_m$ before the activity filter, then zeroing names, leaves a nonzero net residual book.
- **Look-ahead week.** Using this week’s close-to-close as both signal and P&L is a failed spec.

## 11. Acceptance tests

- Two names, residuals $+x$ and $-x$ → equal-magnitude opposite weights, $\sum w_i=0$, $\sum\lvert w_i\rvert=1$.
- Permuting all prices after $t$ must not change the $t$ residual.
- Activity filter: a name in the lower half of $v_i$ is absent from $w$, not zero-weighted inside $R_m$.
- After ADV clipping, neutrality still holds or a residual cash/notional bucket absorbs the gap.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
