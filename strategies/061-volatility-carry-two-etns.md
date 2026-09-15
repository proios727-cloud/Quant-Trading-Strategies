---
rank: 61
slug: volatility-carry-two-etns
title: "Volatility Carry with Two ETNs"
asset_class: "volatility / indexes"
style: "curve-steepness / short front vol ETN vs mid curve"
horizon: "Weeks to months; expect violent drawdowns"
instruments: "VXX (M1–M2 VIX futures ETN), VXZ (M4–M7) or mid-curve VIX futures"
---

# 061. Volatility Carry with Two ETNs

| Field | Value |
|---|---|
| Popularity rank (this kit) | 61 of 101 |
| Why it sits here | Short VXX vs long VXZ (or a mid-curve VIX futures basket). Retail-accessible vol carry; famous for short-VXX squeezes. |
| Aliases | VXX/VXZ, short front vol ETN, mid-curve vol carry |
| Asset class | volatility / indexes |
| Style | curve-steepness / short front vol ETN vs mid curve |
| Typical horizon | Weeks to months; expect violent drawdowns |
| Instruments | VXX (M1–M2 VIX futures ETN), VXZ (M4–M7) or mid-curve VIX futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

VXX holds front VIX futures (M1–M2). VXZ holds mid-curve VIX futures (M4–M7). Both ETNs lose from contango roll; VXX loses more because the VIX curve is usually steeper at the front. Short VXX, long VXZ with a regression hedge ratio. Expect violent drawdowns when the curve flips to backwardation.

Hard risk limits. Short-VXX has unbounded theoretical loss. Model borrow. You are not running file 031’s UX1 hysteresis as a single-contract timer, and you are not selling listed straddles (file 030). You are harvesting the difference in roll cost between the front of the VIX curve and the mid curve, with a hedge that is estimated, not 1:1 dollars.

Typical users are vol-carry sleeves that can survive a VXX squeeze or that pre-commit a flatten rule. Horizon is weeks to months. ETNs close and accelerate; check that the products still exist. Delay-1: $h$ from a window ending at $t$, fill next close. Sharpe without the spike path is not an acceptance of the spec.

## 2. First principles

A VIX-futures ETN is a mechanically rolling long in a strip of UX contracts. In contango each roll sells a cheaper deferred contract and buys a richer nearby contract, so the NAV drifts down. The front of the curve is typically steeper than the mid curve, so VXX’s roll cost exceeds VXZ’s.

A dollar-neutral short VXX / long VXZ is then a bet that this steepness persists. Because the two NAVs have different vol, a 1:1 dollar book is not a vol-neutral book. The OLS hedge of VXX returns on VXZ returns supplies the ratio

$$
h = \beta = \rho\,\sigma_X / \sigma_Z
$$

This is the slope of $X$ on $Z$ when there is an intercept in the usual OLS identity $\beta=\rho\sigma_X/\sigma_Z$ for the two-variable case. Fit only on a window that ends before the fill. Short 1 unit of VXX, long $h$ units of VXZ. When the curve inverts, both ETNs can rally and the short VXX leg dominates. Averaging a short-VXX loser is how the book dies.

That is the whole trade. Everything below is the futures-basket alternative, the spike protocol, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $X$ | VXX (front ETN) |
| $Z$ | VXZ (mid-curve ETN) |
| $\sigma_X,\sigma_Z$ | trailing vols of $X$ and $Z$ returns |
| $\rho$ | trailing correlation of $X$ and $Z$ returns |
| $h=\beta$ | hedge ratio, VXZ per 1 VXX short |
| $C$ | covariance matrix of mid-curve VIX futures returns |
| $w_i$ | weights on $N$ mid-curve VIX futures (basket variant) |
| $I$ | gross dollars |
| $D_X, D_Z$ | signed dollar holdings ( $D_X<0$ in the default book ) |

## 4. Mathematics

### 4.1 OLS hedge (ETN pair)

On a trailing window that **ends before** the fill, with intercept, regress VXX returns on VXZ returns. The slope is

$$
h = \beta = \rho\,\sigma_X / \sigma_Z
$$

If $\rho=1$ and $\sigma_X=2\sigma_Z$, then $h=2$: you need twice as many VXZ dollars per VXX short to match vol. Calm-window $h$ will understate crash convexity. Short 1 VXX, long $h$ VXZ. Dollar holdings with gross $I$:

$$
D_X = -\frac{I}{1+h}, \qquad D_Z = \frac{h I}{1+h}
$$

so $\lvert D_X\rvert+\lvert D_Z\rvert=I$ and $D_Z=-h D_X$. Rebuild $h$ only on data dated $\le t$. Using $t+1$ returns in the window is look-ahead. If borrow on VXX is missing, $D_X$ cannot be short; the blotter is flat, not a “synthetic” option overlay (that is a different spec).

### 4.2 Futures-basket hedge

Replace VXZ with $N$ mid-curve VIX futures. Weights

$$
w_i = \sigma_X \sum_j C^{-1}_{ij} \sigma_j \rho_j
$$

where $C$ is the futures-return covariance, $\sigma_j$ futures vols, $\rho_j$ correlations of VXX with each future, all on a window ending at $t$. This is a minimum-variance basket against VXX, not a 1/N strip. Optional $w_i\ge 0$ and dollar-neutrality $\sum_i w_i=1$ on the long futures sleeve against a short VXX sleeve. Rebalance monthly or more often. Invert $C$ only if it is well-conditioned; a singular $C$ means fewer contracts, not a pseudoinverse alpha.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = D_X R_X^{\mathrm{fwd}} + D_Z R_Z^{\mathrm{fwd}} - \mathrm{borrow} - \mathrm{costs}
$$

Futures variant replaces the $Z$ leg with $\sum_i D_i R_i^{\mathrm{fwd}}$. Report return on $I$, max drawdown, days in backwardation, and borrow fees. Sharpe without the spike path is not an acceptance of the spec. Borrow is first-order: a “free” short VXX in the engine is not this book.

## 5. Step-by-step algorithm

1. **Instruments.** Default: VXX and VXZ. Alternative: short VXX, long UX4–UX7. Check the products still exist; ETNs close. This step exists because a terminated ticker will look like a stale NAV, not a trade.
2. **Hedge.** Estimate $h$ (or $w_i$) on a 60–126 day window ending at $t$. Do not include the fill day. A 1:1 dollar book is not the default.
3. **Size.** Gross $I$ with a hard cap so a 2008-like VIX event fits $L_{\max}$. Cap leverage. Quiet-sample $h$ is not a reason to raise $I$.
4. **Borrow.** Short VXX only if borrow is available; fee into expected P&L. Missing borrow → no short in the blotter.
5. **Blotter.** Shares / contracts, round, emit intents. Do not route live orders.
6. **Spike protocol.** Flatten or cut to a minimum when VIX or the VXX/VXZ ratio breaches a pre-committed rule. Do not average a short-VXX loser. The rule is frozen before the first fill.
7. **Rebalance.** Monthly, or when $h$ drifts by more than a tolerance. Daily OLS on two ETNs is turnover.
8. **Delay.** Decision data strictly before $t_{\mathrm{fill}}$.

## 6. Execution protocol

- Default fill: next close after $h$ is known. Delay-0 is research-only.
- Re-estimate $h$ on a trailing window. Cap gross leverage.
- Flatten on a VIX spike protocol. Do not average a short-VXX loser.
- Model borrow. A “synthetic short” via options is a different spec.

## 7. Data contract

Required, point-in-time:

- VXX and VXZ (or mid-curve VIX futures) prices, returns, volumes
- Borrow availability and fees for short VXX
- VIX spot for the spike protocol
- Product existence / acceleration events for the ETNs

Not used by this spec: equity book value, earnings, SUE, single-name option chains, COT.

No look-ahead on $h$: the regression window ends at $t$, not at $t+1$. Acceleration or close events known after $t$ do not change the $t$ blotter except as a halt that prevents a fill.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| hedge lookback | 60–126 days | ends before fill |
| variant | VXX/VXZ pair | or UX4–UX7 |
| $w_i\ge 0$ | optional | futures variant |
| leverage cap | caller-set | hard $L_{\max}$ |
| spike protocol | on | flatten rule pre-committed |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.volatility_carry_two_etns` with:

1. `hedge_ratio(R_X, R_Z, window) -> float` — $h=\rho\sigma_X/\sigma_Z$ on a window ending at $t$.
2. `futures_weights(sigma_X, C, sigmas, rhos) -> pd.Series` — $w_i$ from 4.2.
3. `holdings(h, I) -> dict` — $D_X,D_Z$ with $\lvert D_X\rvert+\lvert D_Z\rvert=I$.
4. `blotter(holdings, prices, lot, borrow) -> list[OrderIntent]` — refuse the short if borrow is missing; never live routing.
5. `pnl(D, forward_returns, borrow, costs) -> float` — matches 4.3.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **VXX squeeze.** Backwardation and buy-ins; theoretical loss on the short is unbounded. The spike protocol is mandatory because of this, not optional decoration.
- **Curve flip.** Contango can become backwardation for weeks. Roll-down assumed in the overview is then a roll-up you are short.
- **ETN issuer / close.** Products terminate; the pair disappears. Treating a last NAV as tradable is a failed spec.
- **Tracking.** ETN NAV versus VIX is not a basis you can deliver. File 031’s $B_{\mathrm{VIX}}$ is not this P&L.
- **Borrow.** A locate that vanishes mid-hold turns the book into leftover long VXZ.
- **Look-ahead $h$.** Fitting through the crash week to size the pre-crash short uses the outcome as the hedge.

## 11. Acceptance tests

- Toy vols $\sigma_X=2\sigma_Z$, $\rho=1$ → $h=2$.
- Holdings: $D_Z=-h D_X$ and $\lvert D_X\rvert+\lvert D_Z\rvert=I$ to `1e-8`.
- Permuting returns after $t$ must not change $h_t$.
- Missing borrow → no short VXX in the blotter.
- Adding linear costs $\tau$ or borrow fees weakly decreases P&L.
- A backtest that drops all days with VIX above a cap is not a pass.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
