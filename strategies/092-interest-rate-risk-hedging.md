---
rank: 92
slug: interest-rate-risk-hedging
title: "Interest Rate Risk Hedging with Futures"
asset_class: "futures / commodities"
style: "DV01 hedge / bond vs rates futures"
horizon: "Inventory holding period"
instruments: "cash bonds; T-bond / T-note futures"
---

# 092. Interest Rate Risk Hedging with Futures

| Field | Value |
|---|---|
| Popularity rank (this kit) | 92 of 101 |
| Why it sits here | Hedge bond inventory with T-bond/T-note futures via conversion-factor or duration hedge ratios. |
| Aliases | Treasury futures hedge, conversion-factor hedge, DV01 hedge |
| Asset class | futures / commodities |
| Style | DV01 hedge / bond vs rates futures |
| Typical horizon | Inventory holding period |
| Instruments | cash bonds; T-bond / T-note futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Hedge a cash-bond inventory with T-bond or T-note futures. Long the futures if you need to hedge a future **increase** in the bond price (yields down); short the futures to hedge a price decrease (yields up). The hedge ratio comes from conversion factors when the bond is deliverable, or from dollar durations otherwise.

This is a hedge spec. Residual is CTD optionality, curve shape, and basis. You are not running a fly (file 083) or a swap-spread package (file 084). You are offsetting inventory DV01 with listed rates futures. File 090 is commodity quantity matching; this file is rates DV01 matching.

Typical users are dealers and portfolio managers with cash-bond inventory. Horizon is the inventory holding period, not a Sharpe-seeking hold in the futures leg. Recompute $h$ when $D_B$, $D_F$, or CTD switches. Delay-1: next close after $h$ is known. Do not assume you will deliver unless that is the commercial plan: the delivery option is leftover risk on a short-futures / long-basis package. Margin on futures versus unlevered cash bonds is a cash risk even when DV01 matches. Wrong bucket (ZN versus ZB) is a curve bet labeled as a hedge.

## 2. First principles

Cash bond $S(t)$, futures $F(t,T)$. The quoted basis is

$$
B(t,T)=S(t)-F(t,T)
$$

A one-to-one long hedge (long cash, short one future, $h=1$) has P&L $P_L=B(0,T)-B(t,T)$ at the unwind if notionals match; a short hedge has $P_S=B(t,T)-B(0,T)$. That unit-$h$ identity ignores conversion factors and duration. It is the teaching case, not the working ratio for a 7-year note versus ZB.

Deliverable bonds are hedged with the exchange conversion factor $C$:

$$
h_C = C\,\frac{M_B}{M_F}
$$

$M_B$ and $M_F$ are notionals (cash face versus futures contract size). $C$ is frozen at the decision stamp. Using a later conversion-factor table restates $h_C$. Non-deliverable, or a better first-order match, uses dollar durations $D_B,D_F$ and a relative-yield beta $\beta$:

$$
h_D = \beta\,\frac{D_B}{D_F}
$$

$D$ are **dollar** durations. $\beta$ is the relative yield change of the bond versus the futures CTD (often set to 1; else estimated on a window ending at $t$). Short $h$ futures against a long cash inventory. Modified duration without the price factor is the wrong $D$.

That is the whole hedge. Everything below is CTD, re-hedge, and how not to look ahead. If you skip $C$ on a deliverable and use $h=1$, conversion-factor risk is unlabeled inventory. If you skip dollar duration and use modified duration, $h_D$ is off by a price factor. If you skip CTD identity, a switch will look like unexplained P&L rather than a discrete jump in $D_F$.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S(t)$ | cash bond dirty price (or quoted as used in $B$) |
| $F(t,T)$ | T-bond / T-note futures price |
| $B(t,T)=S(t)-F(t,T)$ | quoted basis |
| $C$ | conversion factor of the cash bond (if deliverable) |
| $M_B, M_F$ | cash and futures notionals |
| $D_B, D_F$ | dollar durations of bond and futures (CTD) |
| $\beta$ | relative yield change, bond vs CTD |
| $h_C, h_D$ | conversion-factor and duration hedge ratios |
| $Q$ | signed futures contracts |

## 4. Mathematics

### 4.1 Basis P&L at $h=1$

Basis $B(t,T)=S(t)-F(t,T)$. Long-hedge P&L $P_L=B(0,T)-B(t,T)$; short-hedge $P_S=B(t,T)-B(0,T)$ at unit $h=1$. This identity is a check that notionals match and that you did not flip a sign. It is not $h_C$ or $h_D$. Using it as the working hedge on a non-CTD note will leave a large DV01 residual.

### 4.2 Conversion-factor ratio (deliverable)

$$
h_C = C\,\frac{M_B}{M_F}
$$

Use $h_C$ on CTD-basket futures when the inventory bond is in the delivery basket. $C$ is the exchange conversion factor, frozen at the decision stamp. A CTD switch changes both $C$ and $D_F$; recompute. Do not assume you will deliver unless that is the commercial plan: the delivery option is residual risk on a short-futures / long-basis package.

### 4.3 Modified-duration ratio (deliverable or not)

$$
h_D = \beta\,\frac{D_B}{D_F}
$$

$\beta$ is the relative yield change of the bond vs the futures CTD (often set to 1; else estimated). $D$ are **dollar** durations. $h_D$ is the default when the bond is not deliverable. Estimating $\beta$ on a window that includes the hedge period is look-ahead. $\beta=1$, $D_B=D_F$, $M_B=M_F$ implies $h_D=1$, which is the unit test for this line.

### 4.4 Combined P&L

Long inventory, short $h$ futures:

$$
\mathrm{P\&L} = M_B\Delta S - h M_F\Delta F + \mathrm{accrual} - \mathrm{costs}
$$

Recompute $h$ as duration and CTD change. Objective: variance of inventory-plus-futures P&L, not futures Sharpe. Non-parallel curve moves (2s versus 30s with a 10y hedge) are leftover risk. Margin versus cash-bond liquidity: the hedge can demand cash while the bond does not.

## 5. Step-by-step algorithm

1. **Inventory.** Cash bond identity, face $M_B$, long or short, dated $\le t$. This step exists so $h$ is not fit on a position chosen after seeing $\Delta S$.
2. **Contract.** ZN or ZB (or the matching bucket). Pull CTD and conversion factors. Wrong bucket is a curve bet labeled as a hedge.
3. **Ratio.** If deliverable, $h_C$; else $h_D$ with $\beta=1$ default. Mixing $h_C$ on a non-deliverable note is a failed spec.
4. **Sign.** Long inventory → short $h$ contracts; short inventory → long $h$. Sign errors turn the hedge into a double.
5. **Blotter.** Round to contracts, emit intents. Do not route live orders. Residual after rounding is leftover DV01; log it.
6. **Recompute.** When $D_B$, $D_F$, or CTD switches. Frozen $h$ through a CTD switch is a jump in residual.
7. **Delivery option.** Do not assume you will deliver unless that is the commercial plan. Tail risk on the short-futures package remains.
8. **Delay.** Next close after $h$ is known. Delay-0 is research-only.

## 6. Execution protocol

- Default fill: next close. Delay-0 is research-only. Using the fill yield in $D_B$ to size the hedge that trades that yield is look-ahead.
- Use $h_C$ on CTD-basket futures; $h_D$ otherwise. $M_B,M_F$ are notionals. Mixing quoted futures points with decimal bond prices without the multiplier will scale $h$ by 100 or by 1000.
- Account for delivery optionality. A CTD switch is a discrete jump in $h$. Frozen $h_C$ through the switch leaves a DV01 hole overnight.
- Margin versus cash-bond liquidity: the hedge can demand cash while the bond does not. Combined P&L can be fine while the desk is posting VM.

## 7. Data contract

Required, point-in-time:

- Cash bond dirty/clean prices, dollar duration, face
- Futures price, contract size $M_F$, conversion-factor table, CTD identity
- Yields for $\beta$ if $\beta$ is estimated
- Delivery calendar

Not used by this spec: COT as a signal, commodity $\phi$, equity book value, earnings, SUE.

No look-ahead on the next CTD switch. A conversion-factor file dated after $t$ does not change $h_t$. Yields used for $\beta$ must end at $t$ if $\beta$ is estimated. Delivery calendar is required even if you do not plan to deliver: first notice still changes who is CTD and therefore $D_F$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| futures | ZN / ZB | matching bucket |
| $\beta$ | 1 | else trailing estimate |
| $C$ | exchange conversion factor | |
| ratio | $h_C$ if deliverable else $h_D$ | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.interest_rate_risk_hedging` with:

1. `basis(S, F) -> float` — $S-F$.
2. `h_conversion(C, M_B, M_F) -> float` — $h_C$.
3. `h_duration(beta, D_B, D_F) -> float` — $h_D$.
4. `blotter(h, side, lot) -> list[OrderIntent]` — never live routing.
5. `combined_pnl(dS, dF, h, M_B, M_F, costs) -> float` — matches 4.4.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **CTD switch.** $h_C$ and $D_F$ jump. Frozen ratios through the switch leave a discrete DV01 hole.
- **Non-parallel curve.** Duration match is a local parallel identity. A 2s30s twist versus a 10y future is leftover risk.
- **Delivery option.** Tail risk on the short-futures / long-basis package. Assuming delivery is free is not this spec.
- **Margin.** Futures VM versus unlevered cash-bond inventory. Combined P&L can be fine while cash is not.
- **Wrong $D$.** Using modified duration without multiplying by price leaves $h_D$ off by a factor of $S/100$.
- **Look-ahead CTD.** Using tomorrow’s deliverable to set today’s $h$ restates the hedge.

## 11. Acceptance tests

- $h_C=C M_B/M_F$ and $h_D=\beta D_B/D_F$ to `1e-8`.
- $\beta=1$, $D_B=D_F$, $M_B=M_F$ → $h_D=1$.
- Unit $h=1$ long-hedge P&L equals $B(0,T)-B(t,T)$ on a toy path where notionals match.
- Permuting next day’s CTD must not change $h_t$.
- Adding linear costs $\tau$ weakly decreases combined P&L.
- Combined-book variance is the objective; futures-leg Sharpe is not a pass.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
