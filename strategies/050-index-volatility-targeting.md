---
rank: 50
slug: index-volatility-targeting
title: "Index Volatility Targeting with Risk-Free Asset"
asset_class: "volatility / indexes"
style: "constant-vol overlay / risk scaling"
horizon: "Weekly or monthly rebalance, or on a drift trigger"
instruments: "equity index (futures or ETF) plus T-bills / cash"
---

# 050. Index Volatility Targeting with Risk-Free Asset

| Field | Value |
|---|---|
| Popularity rank (this kit) | 50 of 101 |
| Why it sits here | Target-vol / risk-control overlays used in risk-parity, CTAs, and vol-controlled indexes. |
| Aliases | target vol, risk control, constant-vol overlay |
| Asset class | volatility / indexes |
| Style | constant-vol overlay / risk scaling |
| Typical horizon | Weekly or monthly rebalance, or on a drift trigger |
| Instruments | equity index (futures or ETF) plus T-bills / cash |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Hold a weight $w=\sigma^\ast/\sigma$ in a risky equity index and $1-w$ in cash so that ex-ante portfolio volatility matches a target $\sigma^\ast$. When forecast vol is high, cut the index; when it is low, raise the index up to a leverage cap $L$.

This is a risk overlay, not a directional forecast. The only signal is the vol estimate. You are not selling the VRP (file 030), not trading UX1 basis (file 031), and not expressing a view that the index will rise. If the index is in a quiet bull market, $w$ may sit at $L$ and the overlay will look like levered beta; that is the design, not a bug to be patched with a trend filter unless a different spec says so.

Typical users are risk-parity books, vol-controlled indexes, and CTA overlays that want a more stable risk budget than raw equity. Horizon is weekly or monthly, or a drift trigger $\kappa$ so you do not trade every 10bp of VIX. Delay-1 is required: the fill-day return must not sit in $\sigma$.

Implied vol is the preferred estimator because it is forward-looking. Realized trailing vol will stay low into the first day of a crash and keep $w$ high. That lag is a first-order risk of this file.

## 2. First principles

Let $R$ be the index excess return with forecast volatility $\sigma$, and let $r_f$ be the cash rate. A portfolio that puts weight $w$ in the index and $1-w$ in cash has excess-return volatility

$$
\sigma_p = \lvert w\rvert\,\sigma
$$

This is the one-factor identity: cash is treated as having zero excess-return vol. If cash vol is not zero (T-bill mark-to-market), $\sigma_p$ is slightly wrong; document that if it matters. The absolute value is there so a forbidden short overlay would still scale; this file takes $w\ge 0$.

Set $\sigma_p$ equal to a target $\sigma^\ast$ and take $w\ge 0$ (long-only overlay):

$$
w = \frac{\sigma^\ast}{\sigma}
$$

If $\sigma>\sigma^\ast$, $w<1$ and the remainder sits in cash. If $\sigma<\sigma^\ast$, $w>1$ is leverage. Without a cap, a quiet sample sends $w$ to infinity. Units must match: both $\sigma$ and $\sigma^\ast$ annualized, both decimal or both percent. Mixing them scales $w$ by 100. Cap $w$ at $L$ so a quiet sample cannot gear the book without bound:

$$
w = \min\bigl(L,\; \sigma^\ast / \sigma\bigr)
$$

$L=1$ means never lever: $w\in[0,1]$. $L=2$ is a common risk-control index cap. If $\sigma\to 0$, $w$ hits $L$, not infinity. The min is the whole leverage policy; clipping after the fact in the blotter without recording $L$ will not match tests.

The cash weight is the residual

$$
w_{\mathrm{rf}} = 1-w
$$

which is negative when $w>1$. Negative cash is borrow. Do not assume you borrow at $r_f$; use a documented funding rate. Forecast $\sigma$ from implied vol (preferred, forward-looking) or from a trailing realized estimator that ends before the fill. That is the whole overlay. Everything below is the estimator, the rebalance trigger, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $\sigma$ | forecast of index volatility (implied or realized) |
| $\sigma^\ast$ | target volatility |
| $L$ | max leverage on the index |
| $w$ | weight in the risky index |
| $w_{\mathrm{rf}}$ | weight in cash / T-bills |
| $\kappa$ | relative-drift trigger for rebalancing |
| $I$ | NAV (dollars) |
| $D_{\mathrm{idx}}$ | dollar holding in the index, $D_{\mathrm{idx}}=w I$ |
| $F$ | index future used as the overlay (optional) |

## 4. Mathematics

### 4.1 Vol forecast

Let $\sigma$ be implied (preferred) or a forecast of index vol on a window that **ends before** $t_{\mathrm{fill}}$. Implied: ATM or VIX-style index vol, in annualized decimal. Realized alternative: trailing standard deviation of log returns with $F=252$, or an EWMA. Do not mix units: $\sigma$ and $\sigma^\ast$ are both annualized. Including the fill-day return in realized $\sigma$ is look-ahead and also double-counts the first holding-period move as if it were known in advance. Two-sided filters on the full sample are forbidden.

### 4.2 Target-vol weights

$$
w = \min\bigl(L,\; \sigma^\ast / \sigma\bigr)
$$

If $\sigma=\sigma^\ast$, $w=1$ before the cap binds. If $\sigma=2\sigma^\ast$ and $L\ge 1$, $w=1/2$. If $\sigma=\sigma^\ast/10$ and $L=2$, $w=2$, not $10$. Those three cases are the unit tests for this line.

Cash residual:

$$
w_{\mathrm{rf}} = 1-w
$$

If $L=1$, the overlay never levers: $w\in[0,1]$. If $\sigma\to 0$, $w$ hits $L$, not infinity. When $w_{\mathrm{rf}}<0$, the blotter must show borrow, not a vanishing cash line.

### 4.3 Rebalance trigger

Optional: skip a trade unless the proposed weight has drifted enough since the last fill:

$$
\frac{\lvert w_t - w_{\mathrm{last}}\rvert}{\lvert w_{\mathrm{last}}\rvert} > \kappa
$$

If $w_{\mathrm{last}}=0$, rebalance whenever $w_t>0$. Calendar rebalance (weekly or monthly) is the default if the trigger is off. The trigger exists to cut turnover when $\sigma$ flickers around $\sigma^\ast$. It is not a permission to freeze $w$ through a crash: a large jump in $\sigma$ will breach $\kappa$ and should trade.

### 4.4 Holding-period P&L

NAV return from fill to next rebalance:

$$
\mathrm{P\&L} = D_{\mathrm{idx}} R_{\mathrm{idx}}^{\mathrm{fwd}} + (I-D_{\mathrm{idx}}) r_f\Delta t - \mathrm{costs}
$$

Futures overlay: $D_{\mathrm{idx}}$ is notional; cash stays in T-bills and variation margin is settled daily. If $w>1$, replace $r_f$ on the borrowed slice with the actual funding rate or the P&L identity is too kind. Report return on $I$, realized vol versus $\sigma^\ast$, and turnover.

$$
\mathrm{turnover}_t = \frac{1}{2}\lvert w_t - w_{t-1}\rvert
$$

One-way turnover on a single overlay weight is half the absolute change. High turnover with a realized-vol estimator that jumps every day is a cost leak, which is why $\kappa$ or a weekly calendar exists.

## 5. Step-by-step algorithm

1. **Index.** One equity index via futures (preferred, cheaper) or an ETF plus T-bills. This step exists so the overlay is a single $\sigma$, not a book of names with a blended vol you did not define.
2. **Forecast.** Compute $\sigma$ from implied vol or from returns dated $\le t < t_{\mathrm{fill}}$. The end-before-fill rule is the look-ahead gate. Implied and realized must not be averaged in silence; pick one per run.
3. **Weight.** $w=\min(L,\sigma^\ast/\sigma)$, $w_{\mathrm{rf}}=1-w$. Units of $\sigma$ and $\sigma^\ast$ must already match before this line. Do not clip $w$ a second time in the blotter without changing $L$.
4. **Trigger.** If the $\kappa$ rule is on and drift is below $\kappa$, keep the previous overlay. Skipping this check will overtrade a noisy realized estimator.
5. **Size.** $D_{\mathrm{idx}}=w I$. Cap futures by liquidity. If $w>1$, borrow cash at a documented rate, not at $r_f$ by assumption. Liquidity caps that cut $D_{\mathrm{idx}}$ change realized vol versus $\sigma^\ast$; log that.
6. **Blotter.** ETF shares or futures contracts, round to lot, emit intents. Do not route live orders. Rounding should not silently drop the cash residual.
7. **Cash.** Sweep $w_{\mathrm{rf}} I$ into T-bills (or leave as uninvested cash in a futures overlay). Forgetting the cash leg turns the spec into a floating-notional futures bet with no NAV identity.
8. **Rebalance.** Weekly, monthly, or on the $\kappa$ trigger. Delay-1. Same-bar VIX-to-trade is research-only.

## 6. Execution protocol

- Default fill: next close after $\sigma$ is known. Delay-0 is research-only.
- Trading the futures overlay is usually cheaper than trading the cash index.
- Do not use a vol forecast that includes the fill-day return.
- After a spike, $\sigma$ lags; the overlay will still be long into the second day of a crash unless implied vol is the estimator.

## 7. Data contract

Required, point-in-time:

- Index level or ETF price, fully adjusted
- Implied vol (VIX or ATM option vol) and/or trailing returns for realized $\sigma$
- Cash / T-bill rate $r_f$
- Futures contract specs if the overlay is listed

Not used by this spec: book value, earnings, SUE, industry maps, single-name residuals, option Greeks beyond the implied-vol input.

No look-ahead on VIX prints or on the realized window. A restated VIX after the close does not change $w_t$. Trailing realized vol must not include returns with timestamp $\ge t_{\mathrm{fill}}$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $\sigma^\ast$ | $10\%$–$15\%$ | annualized |
| $L$ | $1$ (unlevered) or $2$ | cap on $w$ |
| $\kappa$ | $10\%$ of $w$ | trigger off → calendar only |
| rebalance | weekly or monthly | or $\kappa$ |
| $\sigma$ source | implied preferred | realized EWMA allowed |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.index_volatility_targeting` with:

1. `forecast_vol(series, method, t) -> float` — $\sigma$ using only data $\le t$.
2. `weights(sigma, sigma_star, L) -> dict` — $w$ and $w_{\mathrm{rf}}$ matching 4.2, $w=\min(L,\sigma^\ast/\sigma)$.
3. `should_rebalance(w, w_last, kappa) -> bool` — $\kappa$ rule.
4. `blotter(w, I, price, lot) -> list[OrderIntent]` — index/futures plus cash, never live routing.
5. `pnl(D_idx, R_idx, I, r_f, dt, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Lag.** Realized-vol forecasts trail spikes; the overlay stays long into a crash. Implied vol reduces this but can overshoot and cut $w$ after the gap, missing the rebound.
- **Leverage.** $L>1$ after a quiet sample, then $\sigma$ jumps. The cap is what bounds that; raising $L$ because recent realized vol was low is circular.
- **Cash drag.** $w<1$ earns $r_f$, which can be below the index. That is the cost of the risk budget, not a bug to be “fixed” by forcing $w=1$.
- **Estimator break.** Mixing percent-vol with decimal $\sigma^\ast$ scales $w$ by 100. A $w=15$ overlay is almost always a units bug.
- **Look-ahead window.** Including the fill bar in $\sigma$ uses the first loss to size the position that took the loss.
- **Funding.** Levered overlays that finance at $r_f$ in the engine and at a spread in reality overstate P&L.

## 11. Acceptance tests

- $\sigma=\sigma^\ast$ → $w=1$, $w_{\mathrm{rf}}=0$.
- $\sigma=2\sigma^\ast$, $L\ge 1$ → $w=1/2$.
- $\sigma=\sigma^\ast/10$, $L=2$ → $w=2$, not $10$.
- Permuting returns and VIX after $t$ must not change $\sigma_t$ or $w_t$.
- Adding linear costs $\tau$ weakly decreases P&L.
- A realized estimator whose window includes the fill timestamp must be rejected.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
