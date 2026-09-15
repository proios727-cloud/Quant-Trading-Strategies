---
rank: 34
slug: bond-immunization
title: "Bond Immunization"
asset_class: "fixed income"
style: "ALM / duration match to a liability"
horizon: "Liability date $T^\ast$; periodic rebalance"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 034. Bond Immunization

| Field | Value |
|---|---|
| Popularity rank (this kit) | 34 of 101 |
| Why it sits here | Reddington immunization. Default toolkit for matching a known future obligation when a zero of that maturity is unavailable. |
| Aliases | Reddington immunization, ALM duration match |
| Asset class | fixed income |
| Style | ALM / duration match to a liability |
| Typical horizon | Liability date $T^\ast$; periodic rebalance |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A liability of face $F$ due at $T^\ast$ can be matched with a zero of that maturity. When that zero is unavailable, build a coupon-bond portfolio whose present value equals the discounted obligation and whose (modified) duration equals the liability’s duration. Two bonds match value and duration; three can also match convexity.

This is an ALM hedge, not a Sharpe trade. The objective is surplus variance near zero under parallel shocks, not a high return on surplus. Rebalance as yields and time move. You are not running the roll-down harvest in file 035 or the carry factor in file 057: those seek income from a static curve. This file exists to pay $F$ at $T^\ast$.

Typical users are ALM desks, insurers, and pension overlays that cannot buy a STRIP of maturity $T^\ast$ in size. Horizon is the liability date, with periodic rebalance when duration drift exceeds a tolerance. Delay-1 solves are the research default.

A single callable credit is a poor asset for this job: optionality is not in textbook $D$ unless modelled. Prefer a barbell of liquid governments, or a ladder, and document credit if you use it.

## 2. First principles

Work in periodic compounding with period $\delta$ and yield $Y$ per period. The present value of an obligation $F$ at $T^\ast$ is

$$
P = \frac{F}{(1+Y\delta)^{T^\ast/\delta}}
$$

This is the cash you must hold, in present-value units, to meet $F$ if $Y$ is the discount rate. A different compounding convention is a different $P$. Mixing annual $Y$ with semi-annual $\delta$ will mis-size the whole book. Freeze $Y$ from the curve dated $\le t$; a later close does not restate the $t$ liability.

Macaulay duration of that liability, in years, is $T^\ast$; modified duration is

$$
D = \frac{T^\ast}{1+Y\delta}
$$

Modified duration is the coefficient in $\Delta P \approx -P D\Delta Y$. For a zero-like liability the Macaulay date is $T^\ast$ itself. If you match Macaulay on the assets to $T^\ast$ but forget the $1+Y\delta$ conversion, the dollar sensitivities will not match.

A coupon bond’s price moves, to first order, as $\Delta P_c \approx -P_c D_c \Delta Y$. A portfolio of holdings $P_k$ (dollars of dirty price) with modified durations $D_k$ matches the liability to first order when two constraints hold: value and duration.

$$
\sum_k P_k = P
$$

Value matching says the assets can pay the PV of $F$ today. Without it, duration matching alone can still leave you underfunded. Holdings $P_k$ are dirty-price dollars, not par amounts and not quoted prices per 100.

The duration constraint is

$$
\sum_k P_k D_k = P D
$$

Then a small **parallel** shift in $Y$ moves the assets and the liability by the same dollars. That is Reddington immunization. It does not kill non-parallel shifts, yield differences across bonds, or reinvestment risk between rebalances. Coupons received before $T^\ast$ are reinvested at unknown rates; that is why you rebalance rather than set and forget.

That is the whole construction. Everything below is the two-bond and three-bond systems, the rebalance rule, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $F$ | liability face due at $T^\ast$ |
| $T^\ast$ | liability date |
| $Y$ | yield used to discount the liability (periodic) |
| $\delta$ | compounding period (e.g. $1/2$ for semi-annual) |
| $P$ | present value of the liability |
| $D$ | modified duration of the liability |
| $C$ | convexity of the liability (three-bond mode) |
| $P_k$ | dirty-price dollars in bond $k$ |
| $D_k$ | modified duration of bond $k$ |
| $C_k$ | convexity of bond $k$ |
| $P(t,T)$ | zero price |
| $P_c(t,T)$ | coupon-bond dirty price |
| $\mathrm{DD}=\mathrm{ModD}\cdot P_c$ | dollar duration |

## 4. Mathematics

### 4.1 Liability

Periodic compounding, period $\delta$. Obligation $F$ at $T^\ast$, yield $Y$:

$$
P = F / (1+Y\delta)^{T^\ast/\delta}
$$

This is the same identity as Section 2, written for the solver. If $T^\ast/\delta$ is not an integer, document the day-count rather than rounding in silence. Modified duration of the liability is

$$
D=T^\ast/(1+Y\delta)
$$

A one-period bump in $Y$ must move $P$ by about $-P D$ in a unit test. If it does not, the compounding in $P$ and in $D$ is inconsistent.

Coupon bonds on the asset side use the usual zero decomposition

$$
P_c(t,T)=P(t,T)+k\delta\sum_{i=I(t)}^n P(t,T_i)
$$

Dirty price is what you hold. Using clean prices in $P_k$ while $P$ is a full PV will overstate or understate surplus by accrued.

### 4.2 Two-bond match

Choose two bonds with present values $P_1,P_2$ (the dollar holdings, not the quoted prices per 100). Solve

$$
P_1+P_2=P
$$

and

$$
P_1 D_1 + P_2 D_2 = P D
$$

A barbell ($D_1<D<D_2$) is the usual geometry: one bond shorter than the liability, one longer. If $D_1=D_2$ the duration equation is redundant and immunization needs a different pair. If the mandate is long-only and the solve wants a negative $P_k$, refuse and pick another set; do not silently short a bond the ALM policy forbids.

### 4.3 Three-bond match (convexity)

Liability convexity under the same compounding is

$$
C=T^\ast(T^\ast+\delta)/(1+Y\delta)^2
$$

Convexity is the second derivative of PV with respect to yield, scaled in the usual textbook way. Two-bond mode leaves a convexity gap versus a liability zero, especially if the barbell is wide. Three holdings also match convexity:

$$
\sum_{k=1}^3 P_k = P
$$

Value is still matched; adding a third bond is not an excuse to drift from $P$.

$$
\sum_{k=1}^3 P_k D_k = P D
$$

Duration remains the first-order hedge. Without it, matching convexity alone is meaningless.

$$
\sum_{k=1}^3 P_k C_k = P C
$$

This still assumes a single $Y$ and a parallel shift. Heterogeneous yields across bonds break the textbook $Y$. Use each bond’s own yield for $D_k$ and $C_k$ and a curve-implied $Y$ for the liability, or document a single-$Y$ textbook mode as research-only.

### 4.4 Holding-period P&L and surplus

Surplus is asset dirty value minus liability PV, minus financing and costs:

$$
\mathrm{surplus} = \sum_k P_k - P - \mathrm{costs}
$$

Duration P&L on each bond is $\approx -\mathrm{DD}\,\Delta y$. Report surplus, residual duration $\sum P_k D_k - P D$, and residual convexity in three-bond mode. The objective is surplus variance near zero under parallel shocks, not a high Sharpe on surplus. A test that “passes” because surplus Sharpe is high has optimized the wrong object.

## 5. Step-by-step algorithm

1. **Liability.** Freeze $F$, $T^\ast$, $\delta$, and $Y$ from the curve dated $\le t$. Compute $P$, $D$, and (if three-bond) $C$. This step exists so the target is known before any asset is chosen. A liability that uses tomorrow’s $Y$ is look-ahead.
2. **Assets.** Pick two or three liquid government (or credit) bonds whose durations straddle $D$. A pair that does not straddle cannot barbell. Callables and sinking bonds need a modelled $D_k$, not a quoted modified duration that ignores optionality.
3. **Solve.** Two-bond: the $2\times 2$ system in 4.2. Three-bond: the $3\times 3$ system in 4.3. Refuse a solve that needs a short if the mandate is long-only; pick another set of bonds. Do not clip a negative holding to zero and call it immunized.
4. **Costs.** Haircut the target by expected transaction costs so the post-trade surplus is not eaten on day one. Ignoring bid/ask makes the first rebalance look like a free surplus gain.
5. **Blotter.** Convert $P_k$ to face value, round to the increment, emit intents. Do not route live orders. After rounding, recompute residual duration; that residual is the true hedge error.
6. **Drift.** Each bar recompute $D_{\mathrm{port}}=\sum P_k D_k / \sum P_k$ and $P$ as $Y$ and time move. Time itself shortens Macaulay duration. A static face book is not immunized a month later.
7. **Rebalance.** Trade only if $\lvert D_{\mathrm{port}}-D\rvert$ exceeds a tolerance, or on a calendar (monthly). Include costs in that rule. Trading every tick of $Y$ is not Reddington; it is a turnover engine.
8. **Horizon.** Stop at $T^\ast$ or when the liability is paid. Keep delisted/called bonds until the event date (no survivorship). Dropping a called bond from history as if it were never held overstates how well surplus was controlled.

## 6. Execution protocol

- Default fill: next close after the solve. Delay-0 is research-only.
- Prefer a barbell-plus-body or a ladder, not a single callable credit.
- Rebalance when duration drift exceeds the tolerance. Do not trade every tick of $Y$.
- Heterogeneous yields across bonds: either use each bond’s own yield for its $D_k$ and a curve-implied $Y$ for the liability, or document a single-$Y$ textbook mode as research-only.

## 7. Data contract

Required, point-in-time:

- Liability schedule $(F,T^\ast)$
- Clean/dirty prices, accrued, coupons, yields
- Modified duration and convexity on each candidate bond
- Compounding convention $\delta$
- Transaction costs and any repo if leverage is used

Not used by this spec: equity book value, earnings, SUE, VIX, option chains, COT, CDS (unless a credit bond’s duration is OAS duration from a documented model).

No look-ahead on calls, sinks, or revised curves after $t$. A call announced at $t+1$ does not change the $t$ $D_k$. Using the terminal path of $Y$ to pick which two bonds “would have worked” is not immunization; it is hindsight.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| mode | two-bond | three-bond adds convexity |
| $\delta$ | $1/2$ | match the market convention |
| rebalance | $\lvert D_{\mathrm{port}}-D\rvert$ tolerance | caller-set |
| long-only | on | shorts only if the mandate allows |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bond_immunization` with:

1. `liability(F, T_star, Y, delta) -> dict` — $P$, $D$, and $C$ matching Section 4.1 and 4.3.
2. `two_bond(P, D, D1, D2) -> tuple` — $(P_1,P_2)$ solving the value and duration equations to `1e-8`.
3. `three_bond(P, D, C, Ds, Cs) -> tuple` — $(P_1,P_2,P_3)$ solving all three constraints to `1e-8`.
4. `blotter(holdings, prices, lot) -> list[OrderIntent]` — face amounts, never live routing.
5. `surplus(assets, P, costs) -> float` — $\sum P_k - P - \mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Non-parallel shifts.** Immunization is a local parallel identity. A steepener can move surplus even with a perfect two-bond match.
- **Yields not equal.** One $Y$ for assets and liability is a textbook convenience. Credit spreads and specials break it.
- **Reinvestment and costs.** Coupons between rebalances and bid/ask eat surplus. A zero-cost backtest overstates how tightly $F$ was matched.
- **Convexity mismatch.** Two-bond mode is short convexity versus a liability zero if the barbell is wide. Large parallel moves then hurt surplus in one direction.
- **Credit and calls.** Spreads and optionality are not in $D$ unless modelled. A called barbell wing leaves you with the wrong duration overnight.
- **Wrong objective.** Maximising surplus Sharpe, or treating immunization as a carry trade, is not this spec.

## 11. Acceptance tests

- Liability identity: $P=F/(1+Y\delta)^{T^\ast/\delta}$ and $D=T^\ast/(1+Y\delta)$ to `1e-8`.
- Two-bond solve: $P_1+P_2=P$ and $P_1 D_1+P_2 D_2=P D$ to `1e-8`.
- Three-bond solve: value, duration, and convexity constraints to `1e-8`.
- A parallel $\Delta Y$ applied to assets and liability leaves surplus unchanged to first order (two-bond) or to second order (three-bond) on a toy curve.
- Permuting prices after $t$ must not change the $t$ solve.
- Adding linear costs $\tau$ weakly decreases surplus.
- A long-only mandate must refuse a solve with any $P_k<0$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
