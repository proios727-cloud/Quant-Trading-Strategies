---
rank: 83
slug: dollar-duration-neutral-bond-butterfly
title: "Dollar-Duration-Neutral Bond Butterfly"
asset_class: "fixed income"
style: "curvature / three-bond butterfly"
horizon: "Days to months"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 083. Dollar-Duration-Neutral Bond Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 83 of 101 |
| Why it sits here | Standard curve-curvature trade: long wings, short body, zero net cash and zero net DV01. |
| Aliases | bond butterfly |
| Asset class | fixed income |
| Style | curvature / three-bond butterfly |
| Typical horizon | Days to months |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long the barbell $(T_1,T_3)$ versus short the bullet $T_2$, with $T_1<T_2<T_3$. Constrain the three dirty-price holdings to be dollar-neutral and dollar-duration-neutral. Residual risk is slope and curvature, not parallel level. Body notional is the size knob.

You are betting that the curve’s belly cheapens or richens versus the wings, not that rates go up. File 033 is two-leg slope with one DV01 constraint. This file adds a cash constraint and a third bond so parallel level is killed twice: cash and DV01. You are not immunizing a liability (file 034); there is no $F$ at $T^\ast$.

Typical users are rates RV desks running 2s5s10s or 5s10s30s flies. Horizon is days to months while the curvature view remains in force. Re-hedge when residual DV01 exceeds a tolerance, not every tick of $Y$. Delay-1: next close after the solve. Fifty-fifty and regression-weighted flies are documented options; mixing them with Section 4.1 silently leaves a cash residual. Same issuer is load-bearing: a credit wing versus a Treasury body is a spread product, not this fly.

## 2. First principles

Three bonds, signed dirty holdings $P_1,P_2,P_3$ (positive = long) and modified durations $D_1,D_2,D_3$. Cash neutrality says the net dirty dollars are zero:

$$
P_1 + P_3 = P_2
$$

(with $P_2>0$ meaning the body is the short if the wings are long: then $P_1>0$, $P_3>0$, and the identity is long wings, short body of matching cash). The cash identity uses dirty dollars, not par amounts. Par-equal wings against a par body will not be cash-neutral once prices differ from 100.

Dollar-duration neutrality says net DV01 is zero:

$$
P_1 D_1 + P_3 D_3 = P_2 D_2
$$

A small parallel $\Delta y$ then cancels to first order. What remains is a bet on curvature (and any slope not spanned by one duration constraint). One duration constraint cannot kill a twist: 2s can rally versus 10s while 5s sit still. Solve the $2\times 2$ system for $P_1,P_3$ given a chosen body size $P_2$.

That is the whole fly. Everything below is the related weight schemes, the re-hedge, and how not to look ahead. If you skip the cash identity, the book has a leftover long or short that is just duration. If you skip the DV01 identity, a parallel day will dominate curvature. If you skip both and equal-weight three bonds, you have a barbell-versus-bullet view with an uncontrolled level bet, which is not this spec.

## 3. Notation

| Symbol | Definition |
|---|---|
| $T_1<T_2<T_3$ | wing, body, wing tenors |
| $P_k$ | signed dirty-price holding in bond $k$ |
| $D_k$ | modified duration of bond $k$ |
| $\mathrm{DD}_k=D_k P_k$ | dollar duration |
| $P(t,T)$ | zero price |
| $P_c(t,T)$ | coupon-bond dirty price |
| $\beta$ | regression or maturity weight in alternative flies |
| $I$ | gross $\lvert P_1\rvert+\lvert P_2\rvert+\lvert P_3\rvert$ |

## 4. Mathematics

### 4.1 Dollar-duration-neutral fly

Given body size $P_2$ (the size knob), solve

$$
P_1 + P_3 = P_2
$$

Cash matching with the body as the scale. If you treat $P_2$ as a long body, the wing signs flip and you have a short-wings fly; keep the intended signs explicit in the solver.

$$
P_1 D_1 + P_3 D_3 = P_2 D_2
$$

This fixes $P_1,P_3$ given $P_2$. Long wings / short body means take $P_1>0$, $P_3>0$, $P_2$ equal to $P_1+P_3$ as a **short** body holding of that cash amount. Immune to small parallel shifts; not immune to slope or curvature changes. After lot rounding, both constraints will drift; residual net DV01 is a reported series.

Coupon bonds use

$$
P_c(t,T)=P(t,T)+k\delta\sum_{i=I(t)}^n P(t,T_i)
$$

and the usual modified durations. Dirty price and duration must share a convention. Mixing clean $P_k$ with dirty $D_k$ breaks both identities.

### 4.2 Related butterflies (not the default)

Fifty-fifty / neutral-curve butterfly sets

$$
P_1 D_1 = P_3 D_3 = P_2 D_2 / 2
$$

which is duration-balanced across wings but **not** dollar-neutral. Calling it cash-neutral in a test that checks Section 4.1 will fail, and should. Regression-weighted uses an empirical $\beta$ on spread changes. Maturity-weighted uses

$$
\beta=(T_2-T_1)/(T_3-T_2)
$$

These variants are documented options; the default book is Section 4.1. $\beta$ here is a tenor ratio, not a look-ahead regression on future yields.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = \sum_{k=1}^3 \Delta P_k + \mathrm{accrual} - \mathrm{repo} - \mathrm{costs}
$$

Duration P&L $\approx -\sum_k \mathrm{DD}_k\Delta y_k$. Report return on $I$, residual net DV01 after rounding, and a PCA residual versus 2s5s10s. Financing of the short body (or short wings, if reversed) is first-order. Special repo on the on-the-run body can dominate curvature P&L.

## 5. Step-by-step algorithm

1. **Tenors.** Default 2s5s10s or 5s10s30s, same issuer. This step exists so a credit wing versus a Treasury body is not called a fly.
2. **Durations.** Pull $D_k$ and dirty prices dated $\le t$. Vendor durations restated next morning do not belong in the $t$ solve.
3. **Solve.** Section 4.1 for chosen $P_2$. Check $P_1,P_3$ have the intended signs. If both wings come out short on a long-wings mandate, the body sign is wrong.
4. **Gross.** Scale so $\lvert P_1\rvert+\lvert P_2\rvert+\lvert P_3\rvert=I$ if $P_2$ was only a shape, not a dollar size. Scaling after the solve preserves the two ratios.
5. **Caps.** Clip by issue size; restore both constraints or bucket the residual. Clipping one wing and leaving the body unchanged is a duration bet.
6. **Blotter.** Face amounts, round, emit intents. Do not route live orders.
7. **Re-hedge.** When yields move enough that net DV01 exceeds a tolerance, re-solve. Time and yield both drift $D_k$.
8. **Delay.** Next close after the solve. Delay-0 is research-only.

## 6. Execution protocol

- Default fill: next close. Delay-0 is research-only. A same-bar solve that uses the fill yield in $D_k$ is look-ahead.
- Re-hedge DV01 when yields move. Watch the fly versus 2s5s10s PCA. If PCA level moves and the fly P&L moves one-for-one, the cash or DV01 constraint is broken.
- Financing of the short body (or short wings, if reversed) is first-order. Specials on the on-the-run body will not show up in a GC-only engine.
- Liquidity of the wings is usually worse than the body. Size $I$ off the worse wing, not off the liquid belly.

## 7. Data contract

Required, point-in-time:

- Clean/dirty prices, yields, modified durations on three bonds
- Repo per leg
- Issue identifiers; conversion factors if futures

Not used by this spec: equity book value, earnings, SUE, CDS, COT.

No look-ahead on CTD or on next day’s durations. A CTD switch announced after $t$ does not change the $t$ futures fly. A vendor duration file that arrives the next morning does not rewrite $D_k(t)$. If you cannot get three point-in-time dirty prices and durations, you cannot run the fly; substituting a fitted par curve for the missing wing is a different book.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenors | 2s5s10s | or 5s10s30s |
| variant | dollar + DV01 neutral | 4.1 |
| fifty-fifty / regression $\beta$ | off | 4.2 |
| $P_2$ | size knob | then scale to $I$ |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.dollar_duration_neutral_bond_butterfly` with:

1. `solve(D1, D2, D3, P2) -> tuple` — $(P_1,P_3)$ matching 4.1 to `1e-8`.
2. `constraints(P, D) -> dict` — net cash and net DV01, both $\approx 0$.
3. `blotter(P, prices, lot) -> list[OrderIntent]` — face, never live routing.
4. `pnl(dP, accrual, repo, costs) -> float` — matches 4.3.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Twist.** One duration constraint does not span slope. A 2s rally versus 10s with 5s unchanged is leftover risk, not a failed solver.
- **Wing liquidity.** Off-the-run 30s versus on-the-run 10s. Screen prices on the long wing are not fills.
- **Financing of shorts.** Special repo on the body. GC-assumed carry overstates the fly.
- **Wrong variant.** Fifty-fifty is not cash-neutral; mixing it with 4.1 silently leaves a cash residual.
- **CTD.** Futures flies jump when the deliverable changes.
- **Look-ahead durations.** Using $t+1$ $D_k$ to set the $t$ fly restates the hedge.
- **Issuer mix.** A G-spread wing versus a Treasury body will look like curvature and then dump on a credit day.
- **Rounding.** Lot increments on the 30-year wing can leave more residual DV01 than the belly; report it, do not assume the solved $P_k$ still hold.

## 11. Acceptance tests

- Solve 4.1: $P_1+P_3=P_2$ and $P_1 D_1+P_3 D_3=P_2 D_2$ to `1e-8`.
- Parallel $\Delta y$ → first-order P&L $=0$ to `1e-6` relative to $I$.
- Maturity-weighted $\beta=(T_2-T_1)/(T_3-T_2)$ is computed from tenors only, not from future yields.
- Permuting yields after $t$ must not change the $t$ solve.
- Adding linear costs $\tau$ weakly decreases P&L.
- Fifty-fifty holdings must fail the Section 4.1 cash identity unless that variant is selected.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
