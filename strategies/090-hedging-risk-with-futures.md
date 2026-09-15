---
rank: 90
slug: hedging-risk-with-futures
title: "Hedging Risk with Futures"
asset_class: "futures / commodities"
style: "commercial hedge / inventory lock"
horizon: "From $t$ to need-date $T$"
instruments: "listed futures"
---

# 090. Hedging Risk with Futures

| Field | Value |
|---|---|
| Popularity rank (this kit) | 90 of 101 |
| Why it sits here | The original futures use-case: lock a purchase or sale price. Airline fuel, grain merchandising, etc. |
| Aliases | commercial hedge, inventory lock, price lock |
| Asset class | futures / commodities |
| Style | commercial hedge / inventory lock |
| Typical horizon | From $t$ to need-date $T$ |
| Instruments | listed futures |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

If you will buy (sell) $X$ units of a commodity at a need-date $T$, buy (sell) futures at $t$ with matching delivery (or the closest liquid contract). Combined with the physical, the book locks a price near $F(t,T)$ if the future is on the same asset and is held to delivery.

This is a hedge spec: minimise variance of the combined commercial-plus-futures book, not maximise Sharpe. You are not picking $X$ to make the futures leg profitable. File 091 is the proxy-hedge case where the future is on a different asset. File 054 is a roll-yield alpha book. This file assumes hedge ratio 1 on the same asset.

Typical users are commercials: airlines hedging fuel, merchandisers locking grain, inventory holders locking a sale. Horizon is from $t$ to the need-date $T$. Roll if $T$ is beyond the liquid contract; do not skip into delivery. Match seasonality (crop year, heating-oil winter) or the leftover basis is a choice, not a surprise. Delay-1: commercial quantity known before the futures fill. Peeking at $S(T)$ to set $Q$ is not a hedge: it is a perfect hindsight lock that will pass every combined-P&L test and fail every look-ahead test.

## 2. First principles

Spot at $T$ is $S(T)$. A long commercial need of $X$ units at $T$ pays $X S(T)$ in the cash market. A long future held to delivery, with $F(T,T)=S(T)$ absent cheapest-to-deliver optionality, has futures P&L per unit $S(T)-F(t,T)$. Combined cash outlay per unit is

$$
S(T) - \bigl(S(T) - F(t,T)\bigr) = F(t,T)
$$

so the purchase is locked at $F(t,T)$. The identity is cash-market purchase minus futures gain. If $F(T,T)\neq S(T)$ because of grade or location, the lock is $F(t,T)$ plus leftover basis, which is file 091 if you chose the wrong contract on purpose. A short commercial inventory (future sale of $X$) is the mirror: short $X$ futures at $t$, lock the sale at $F(t,T)$.

If the future is not held to delivery, or is on a different grade, the lock is $F(t,T)$ plus a remaining basis $S(T)-F(T,T_{\mathrm{fut}})$. Hedge ratio is 1 unless you are cross-hedging (091). Optimising $Q$ on futures Sharpe violates the spec: that turns a hedge into a view.

That is the whole hedge. Everything below is quantity matching, rolls, and how not to look ahead. If you skip matching $Q$ to $X$, leftover physical is unhedged. If you skip the roll calendar, you may be forced into delivery or left with a wrong-month basis. If you skip treating combined variance as the objective, a search will raise $Q$ until the futures leg looks like a profitable view.

## 3. Notation

| Symbol | Definition |
|---|---|
| $X$ | commercial quantity (same units as the future) |
| $T$ | need-date |
| $S(t)$ | spot of the physical |
| $F(t,T)$ | futures price for delivery nearest $T$ |
| $B(t)=S(t)-F(t,T)$ | basis |
| $Q$ | signed futures contracts in physical units (positive = long) |
| $h$ | hedge ratio (1 in this file) |

## 4. Mathematics

### 4.1 Quantity and sign

Long commercial need of $X$ at $T$: long $X$ futures (same units) at $t$.

$$
Q = +X
$$

You buy the future because you will buy the physical: a higher $S(T)$ hurts the commercial and helps the long future. Units must match (barrels, bushels) before the multiplier converts to contracts.

Short commercial inventory / future sale: short $X$ futures.

$$
Q = -X
$$

Hedge ratio $h=1$ unless cross-hedging. $X$ is frozen from the commercial book dated $\le t$. A $Q$ that depends on $S(T)$ is look-ahead and not a hedge.

### 4.2 Locked price and basis

P&L of the combined book converges to locking $F(t,T)$ if the future is on the same asset and held to delivery (basis $\to 0$ at expiry, ignoring cheapest-to-deliver optionality). Before expiry the combined mark is

$$
\mathrm{locked} = F(t,T) + B(\tau)
$$

at intermediate date $\tau$, with $B(\tau)=S(\tau)-F(\tau,T)$. Basis risk is the gap that remains if you lift early, if the grade differs, or if the month is wrong. Report $B$ as a series; hiding it inside “hedge P&L” will look like alpha.

### 4.3 Holding-period P&L

Futures variation margin plus the physical purchase or sale at $T$, minus costs and roll costs if $T$ is beyond the liquid contract:

$$
\mathrm{P\&L}_{\mathrm{combined}} = Q\,\Delta F + X_{\mathrm{sign}}\,S(T) - \mathrm{costs}
$$

$X_{\mathrm{sign}}=-X$ for a purchase (cash out) and $+X$ for a sale. Objective: variance of this combined P&L, not the Sharpe of $Q\Delta F$ alone. A test that maximises futures Sharpe must fail. Margin calls can cash-crunch the hedge even when combined P&L is on track: futures lose cash while the physical is unpriced.

## 5. Step-by-step algorithm

1. **Need.** Freeze $X$, $T$, and buy-versus-sell from the commercial book dated $\le t$. This step exists so $Q$ cannot peek at $S(T)$.
2. **Contract.** Matching delivery, or closest liquid contract with the right seasonality (crop year, heating-oil winter, etc.). Wrong season is basis risk you chose.
3. **Size.** $Q=\pm X$ in physical units, converted to contracts via the multiplier. $h=1$. Rounding to lots leaves a residual commercial slice; log it.
4. **Roll.** If $T$ is beyond the liquid contract, roll along a documented calendar; do not skip into delivery. Roll P&L is part of the lock, not a separate alpha.
5. **Lift.** As the physical is priced, unwind the futures in matching size. Lifting all futures while the physical is only half priced is a leftover view.
6. **Blotter.** Contract intents only. Do not route live orders.
7. **Margin.** Track variation margin versus the unpriced physical; a hedge can still cash-crunch. This is why $L_{\max}$ on cash still matters for a “riskless” lock.
8. **Delay.** Commercial quantity known before the fill. Same-bar $X$ that uses the fill print of $S$ is research-only.

## 6. Execution protocol

- Enter at $t$, lift as the physical is priced. Roll if $T$ is beyond the liquid contract. Roll P&L belongs in the lock; do not book it as a separate “trading” sleeve.
- Match quantity and seasonality (e.g. crop year). Hedge ratio 1 unless cross-hedging. A jet-fuel need hedged with WTI is file 091, even if someone labels it 090.
- Default fill: next close after the need is booked. Delay-0 is research-only.
- This spec does not pick $X$ to maximise expected futures P&L. If a search over $Q$ improves futures Sharpe, the search has left the spec.

## 7. Data contract

Required, point-in-time:

- Commercial quantity $X$, need-date $T$, buy vs sell
- Contract-level futures prices, multiplier, delivery calendar
- Spot $S$ for basis reporting
- Volume / open interest for contract choice

Not used by this spec: COT as a trading signal, 5-year value $v$, equity book value, earnings, SUE.

The commercial $X$ must be known before the futures fill. Peeking at $S(T)$ to set $Q$ is not a hedge. A restated commercial need after $t$ does not change the $t$ $Q$. Spot $S$ is for basis reporting, not for resizing $Q$ after the need is booked. If the closest liquid contract is a different grade, you have left this file and entered 091 even if $h$ is still 1.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $h$ | 1 | cross-hedge is 091 |
| quantity | $X$ | commercial |
| contract | matching delivery | else closest + roll calendar |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.hedging_risk_with_futures` with:

1. `hedge_quantity(X, side) -> float` — $Q=+X$ (buy need) or $Q=-X$ (sell need).
2. `locked_price(F_entry, basis) -> float` — $F(t,T)+B$ identity.
3. `blotter(Q, multiplier, lot) -> list[OrderIntent]` — contracts, never live routing.
4. `combined_pnl(Q, dF, X, S_T, side, costs) -> float` — matches 4.3.
5. `hedge_variance(combined_pnl_paths) -> float` — objective is variance, not Sharpe.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Basis risk.** Grade, location, or timing mismatch. The lock is $F(t,T)+B$, not $F(t,T)$ once those differ.
- **Margin calls.** Futures lose cash while the physical is unpriced. Combined P&L can be fine while the entity is illiquid.
- **Delivery mismatch.** Wrong month or CTD optionality. Heating-oil winter versus summer is not $h=1$ on the same asset in economic terms.
- **Treating the hedge as alpha.** Optimising $Q$ on futures Sharpe violates the spec.
- **Look-ahead $X$.** Setting $Q$ from $S(T)$ is a perfect hindsight lock, not a hedge.
- **Skipping rolls.** Holding a nearby into delivery because “the hedge should go to $T$” can force delivery.

## 11. Acceptance tests

- Buy-need $X$ with $F(T,T)=S(T)$ and $Q=+X$ → combined cost per unit $=F(t,T)$ to `1e-8`.
- Sell-need is the mirror lock.
- Permuting $S(T)$ must not change $Q$ set at $t$.
- Combined-book variance is the reported objective; a higher Sharpe on the futures leg alone is not a pass.
- Adding linear costs $\tau$ weakly decreases combined P&L (worse lock).
- A search that raises $\lvert Q\rvert$ to improve futures-leg Sharpe must fail the hedge-variance objective.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
