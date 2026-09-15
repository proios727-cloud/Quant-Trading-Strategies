---
rank: 91
slug: cross-hedging
title: "Cross-Hedging with Futures"
asset_class: "futures / commodities"
style: "proxy hedge / OLS hedge ratio"
horizon: "Hedge horizon to $T$"
instruments: "listed futures"
---

# 091. Cross-Hedging with Futures

| Field | Value |
|---|---|
| Popularity rank (this kit) | 91 of 101 |
| Why it sits here | When the exact future does not exist, hedge with a correlated contract. Standard in commodity and FX overlays. |
| Aliases | proxy hedge, OLS hedge ratio |
| Asset class | futures / commodities |
| Style | proxy hedge / OLS hedge ratio |
| Typical horizon | Hedge horizon to $T$ |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Hedge an exposure $S$ with a future on a different but related asset $S^\ast$. The optimal ratio is generally not 1. Estimate $h$ by serial regression of $\Delta S$ on $\Delta F$ (minimum-variance). Residual variance after the hedge is the true remaining risk.

This is a hedge spec: minimise variance of $S$ plus the futures leg, not maximise Sharpe on the future. File 090 is $h=1$ on the same asset. This file is the proxy: jet versus heating oil, silver versus gold, a cash asset versus a related listed future. You are not running commodity value or roll yield. Do not pick the proxy by in-sample futures Sharpe.

Typical users are commercials and overlay desks when the exact contract does not exist or is too thin. Horizon is the hedge to $T$. Re-estimate $h$ when it drifts; a frozen ratio through a correlation break is the usual failure. Delay-1: OLS window ends at $t$. Mixing returns with futures points scales $h$ by a price level; the $\Delta$ convention must match the multiplier. Residual variance after the hedge is the risk you still have: report it every time you report P&L, or the book will be judged as if $h=1$ had worked.

## 2. First principles

A unit short future on the hedge asset, held to $T$, pays $F(t,T)-F(T,T)$. With $F(T,T)=S^\ast(T)$ on that asset, rewrite the short-future payoff as

$$
S(T)-F(T,T)+F(t,T)
= \bigl[S^\ast(T)-F(T,T)\bigr] + \bigl[S(T)-S^\ast(T)\bigr] + F(t,T)
$$

The first bracket is the futures–spot basis on the **hedge** asset. The second is the cross-asset residual $S-S^\ast$. The last term is the locked futures price. A unit hedge therefore leaves both a basis and a cross residual. If those brackets are large, $h=1$ from file 090 is the wrong tool, which is why this file exists.

The minimum-variance hedge ratio $h^\ast$ scales the future so that $\mathrm{Var}(\Delta S - h\Delta F)$ is minimised:

$$
h^\ast = \frac{\mathrm{Cov}(\Delta S,\Delta F)}{\mathrm{Var}(\Delta F)}
$$

which is the OLS slope of $\Delta S$ on $\Delta F$ (no intercept, or with intercept — pick one and keep it). $h$ is generally not 1. Fit only on data $\le t$. Using the hedge-horizon path to fit $h$ is look-ahead and will understate residual variance.

That is the whole hedge. Everything below is the window, re-estimation, and how not to look ahead. If you skip the OLS window end-before-fill rule, $h$ will look too good. If you skip residual variance, you will report a “hedge” as if the second bracket were zero. If you skip the $\Delta$ convention, $Q$ will be off by a price level and the combined book will be a large leftover $S$ bet.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S$ | commercial / cash asset to hedge |
| $S^\ast$ | spot of the futures underlier |
| $F(t,T)$ | futures price used as the proxy |
| $h$ | hedge ratio (units of future per unit of $S$) |
| $\Delta S, \Delta F$ | changes over the estimation bar |
| $X$ | commercial quantity of $S$ |
| $Q = -h X$ | futures position in $S^\ast$ units for a long $S$ exposure (short futures) |
| $I$ | notional of $S$ |

## 4. Mathematics

### 4.1 Payoff decomposition

Unit short future payoff at $T$:

$$
S(T)-F(T,T)+F(t,T)
= \bigl[S^\ast(T)-F(T,T)\bigr] + \bigl[S(T)-S^\ast(T)\bigr] + F(t,T)
$$

First bracket: futures–spot basis on the hedge asset. Second: cross-asset residual. Both survive after you choose $h$. Reporting only the futures P&L hides them. Correlation breakdown is the second bracket exploding.

### 4.2 OLS / minimum-variance $h$

Estimate $h$ by serial regression of $\Delta S$ on $\Delta F$ on a window that **ends before** the fill. Equivalent closed form:

$$
h = \frac{\widehat{\mathrm{Cov}}(\Delta S,\Delta F)}{\widehat{\mathrm{Var}}(\Delta F)}
$$

Return versus price-change convention must match the contract multiplier. Optional GARCH or rolling $h$; still fit only on data $\le t$. If $\mathrm{Var}(\Delta F)=0$ on the window, $h$ is undefined; do not divide by zero and emit a huge $Q$. Keep intercept convention consistent with $h=\rho\sigma_S/\sigma_F$ if you use that form.

### 4.3 Position and P&L

Long commercial exposure $X$ in $S$: short $hX$ futures (in matching units). Combined change:

$$
\Delta\mathrm{P\&L} = X\Delta S + Q\Delta F - \mathrm{costs}, \qquad Q=-h X
$$

Report residual variance $\mathrm{Var}(\Delta S-h\Delta F)$, $R^2$ of the hedge regression, and combined P&L. Futures marks are variation margin; include rolls. Objective is residual variance, not a high $R^2$ achieved by peeking. Signs flip for a short commercial exposure.

## 5. Step-by-step algorithm

1. **Exposure.** Freeze $X$ and the identity of $S$ from the commercial book dated $\le t$. This step exists so $h$ cannot be fit on a quantity that was chosen after seeing $S(T)$.
2. **Proxy.** Choose the most liquid related future (documented pair: jet vs HO, silver vs gold, etc.). Do not pick by in-sample Sharpe of $F$.
3. **Window.** 60–252 days of $\Delta S$ and $\Delta F$ ending at $t$. Including the fill bar uses the first hedge-day move twice.
4. **Fit.** OLS $h$ (or the min-var formula). Record residual variance. Residual variance is the risk you still have.
5. **Size.** $Q=-hX$ for a long $S$ book (signs flip for a short exposure). Convert via multipliers. Rounding to lots leaves a residual $X$ slice.
6. **Blotter.** Contract intents, round, emit. Do not route live orders.
7. **Re-estimate.** When $h$ drifts beyond a tolerance, or on a calendar. Frozen $h$ through a correlation break is a known failure mode.
8. **Lift.** Unwind as the physical $S$ is priced. Lifting futures first leaves the cross residual unhedged.

## 6. Execution protocol

- Default fill: next close after $h$ is known. Delay-0 is research-only. Fitting $h$ on a window that includes the fill bar uses the first hedge-day move as if it were known.
- Rebalance $h$ when it drifts. Document residual variance as the true risk. A high in-sample $R^2$ on a calm window is not a promise about a refinery-outage week.
- Optional time-varying $h$ (GARCH) is allowed if the filter is causal. Two-sided filters on the full sample are look-ahead.
- Do not pick the proxy future by in-sample Sharpe. Liquidity and documented economic relation come first; Sharpe of $F$ is the opposite objective.

## 7. Data contract

Required, point-in-time:

- Price series for $S$ and for $F$ (and $S^\ast$ if basis is reported)
- Contract multiplier and calendar
- Commercial quantity $X$
- Volume / open interest for proxy choice

Not used by this spec: COT as a signal, 5-year value $v$, equity book value, earnings, SUE.

No look-ahead in the OLS window. A window that includes $\Delta S$ after $t$ restates $h_t$. Restated cash prices for $S$ must be the vintage available at $t$. Volume and open interest are for choosing a liquid proxy, not for building a COT signal. If $S$ and $F$ are not in comparable units before the regression, convert first; OLS will not magically fix barrels versus gallons.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| OLS lookback | 60–252 days | ends at $t$ |
| intercept | caller-set | keep consistent with $h=\rho\sigma_S/\sigma_F$ |
| $\Delta$ convention | price change | must match multiplier |
| re-estimate | on drift or calendar | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.cross_hedging` with:

1. `hedge_ratio(dS, dF, window) -> float` — OLS / min-var $h$, window ending at $t$.
2. `residual_var(dS, dF, h) -> float` — $\mathrm{Var}(\Delta S-h\Delta F)$.
3. `position(X, h, side) -> float` — $Q$.
4. `blotter(Q, multiplier, lot) -> list[OrderIntent]` — never live routing.
5. `combined_pnl(X, dS, Q, dF, costs) -> float` — matches 4.3.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Correlation breakdown.** The residual $S-S^\ast$ can dominate the risk you meant to cut. Jet versus HO in a refinery outage is the textbook case.
- **Basis + cross residual.** Both brackets in 4.1 survive. $h^\ast$ minimises variance; it does not set those brackets to zero.
- **Wrong $\Delta$ convention.** Mixing returns with futures points scales $h$ by a price level. The book will then be off by a factor of $S$ or $F$.
- **Optimising Sharpe.** Choosing $h$ to make the futures leg profitable is not a hedge.
- **Look-ahead window.** Fitting $h$ through the hedge horizon understates residual variance.
- **Thin proxy.** A liquid $S$ versus an illiquid $F$ makes $h$ look stable on mids and untradeable on size.

## 11. Acceptance tests

- Toy: $\Delta S=2\Delta F$ always → $h=2$, residual variance $0$.
- $h=\mathrm{Cov}/\mathrm{Var}$ to `1e-8` on a toy sample.
- Permuting $\Delta S,\Delta F$ after $t$ must not change $h_t$.
- Combined-book residual variance is reported; futures-leg Sharpe is not a pass criterion.
- Adding linear costs $\tau$ weakly decreases combined P&L.
- $\mathrm{Var}(\Delta F)=0$ must not emit an infinite $Q$.
- Choosing the proxy future by ranking in-sample Sharpe of $F$ must not be accepted as `proxy` selection.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
