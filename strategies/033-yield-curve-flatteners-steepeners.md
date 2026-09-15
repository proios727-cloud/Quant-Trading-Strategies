---
rank: 33
slug: yield-curve-flatteners-steepeners
title: "Yield Curve Spread (Flatteners and Steepeners)"
asset_class: "fixed income"
style: "curve / duration-matched spread"
horizon: "Days to months"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 033. Yield Curve Spread (Flatteners and Steepeners)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 33 of 101 |
| Why it sits here | The standard rates RV trade. Flatteners and steepeners are core FI desk inventory. |
| Aliases | curve spread, 2s10s, flattener, steepener |
| Asset class | fixed income |
| Style | curve / duration-matched spread |
| Typical horizon | Days to months |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Trade the spread between two same-issuer yields of different maturity. A hiking cycle typically flattens the curve (front yields rise more than back yields); an easing cycle typically steepens it. Match dollar durations so a small parallel yield shift cancels and the residual is slope.

You are betting on $\Delta y_b-\Delta y_f$, the change in slope, not on the level of rates. A book that is long equal par amounts of 2s and 10s is mostly a duration bet; that is not this spec. You are also not running the three-leg butterfly in file 083: that kills cash and DV01 and leaves curvature. This file uses two legs and one DV01 constraint.

Typical users are rates RV desks and relative-value sleeves inside FI funds. Horizon is days to months while the policy-path view, or the mean-reversion fade of $s$, remains in force. Rebalance when residual DV01 drifts, not every tick of $Y$. Delay-1 closes are the research default.

Same issuer is load-bearing. Mixing a Treasury front with a credit back converts the slope trade into a credit-spread trade you did not size.

## 2. First principles

A coupon bond’s first-order P&L in a small yield change $\Delta y$ is minus dollar duration times that change:

$$
\Delta P_c \approx -\mathrm{DD}\,\Delta y, \qquad \mathrm{DD} = \mathrm{ModD}\cdot P_c
$$

This is the local linear map from yield to dirty price. It fails for large moves (convexity) and for non-parallel moves (the two legs will not share one $\Delta y$). If you weight by par amount instead of $\mathrm{DD}$, a 10-year will dominate a 2-year on any shared $\Delta y$, and you are back in a level trade.

Two bonds, front tenor $T_f$ and back tenor $T_b>T_f$, with signed dollar holdings $P_{\mathrm{front}}$ and $P_{\mathrm{back}}$ (positive = long). A parallel shift $\Delta y_f=\Delta y_b=\Delta y$ produces

$$
\Delta\mathrm{P\&L} \approx -P_{\mathrm{front}} D_{\mathrm{front}}\Delta y - P_{\mathrm{back}} D_{\mathrm{back}}\Delta y
$$

here $D$ is modified duration so that $P D$ is dollar duration. The two terms add when the shift is parallel. If they do not cancel, the book has a leftover DV01 that will swamp the slope P&L on any decent-sized parallel day. Set the dollar durations equal in magnitude and opposite in sign,

$$
P_{\mathrm{front}} D_{\mathrm{front}} = - P_{\mathrm{back}} D_{\mathrm{back}}
$$

and the parallel piece vanishes. What remains is a bet on $\Delta y_b - \Delta y_f$, the slope. The identity is first-order and local. A butterfly residual (curvature) is not killed by two legs. Coupon timing and repo specials sit outside this display line and still hit P&L.

This file’s sign convention (keep it): **short the spread** means sell the front leg and buy the back leg. That book profits when front yields rise relative to back yields — the usual hiking-cycle flatten. **Buy the spread** is the opposite (buy front, sell back) and profits when the curve steepens from the front rallying.

That is the whole strategy. Everything below is how to measure the two legs, how to keep the DV01 match live, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t,T)$ | zero price |
| $R(t,T)=-\ln P(t,T)/(T-t)$ | continuously compounded zero yield |
| $P_c$ | dirty price of a coupon bond |
| $\mathrm{ModD}$, $\mathrm{MacD}$ | modified and Macaulay duration |
| $\mathrm{DD}=\mathrm{ModD}\cdot P_c$ | dollar duration (DV01 scale) |
| $P_{\mathrm{front}}, P_{\mathrm{back}}$ | signed dirty-price holdings (positive = long) |
| $D_{\mathrm{front}}, D_{\mathrm{back}}$ | modified durations of the two legs |
| $y_f, y_b$ | yields of the front and back bonds |
| $s = y_b - y_f$ | curve spread |
| $I$ | gross dirty-price dollars, $I=\lvert P_{\mathrm{front}}\rvert+\lvert P_{\mathrm{back}}\rvert$ |

## 4. Mathematics

### 4.1 Spread

On the same issuer (default: two Treasuries), the curve spread is

$$
s = y_b - y_f
$$

A flatten is a fall in $s$; a steepen is a rise in $s$. Parallel level is $y_f$ (or a PCA level factor). The trade is not a level trade once DV01 is matched. Mixing yield quotes with different compounding or different settlement conventions will move $s$ without any curve view. Use the same yield type on both legs.

### 4.2 Flattener and steepener

Rule, using only curve information dated before the fill:

- **Flattener** (short the spread), if rates are expected to rise: **sell** the front leg, **buy** the back leg.
- **Steepener** (buy the spread), if rates are expected to fall: **buy** the front leg, **sell** the back leg.

The directional gate can be a simple change in the front yield, a policy-path dummy, or a caller-supplied signal. With no gate, the book is a relative-value fade of $s$ versus its recent mean (long the cheap slope, short the rich slope) still under the same DV01 constraint. Peeking at next month’s FOMC statement to label a “hiking cycle” in a backtest is look-ahead; freeze the gate inputs at $t$.

### 4.3 Dollar-duration match

Weight by DV01, not by par amount. With $D$ modified duration,

$$
P_{\mathrm{front}} D_{\mathrm{front}} = - P_{\mathrm{back}} D_{\mathrm{back}}
$$

On a flattener, $P_{\mathrm{front}}<0$ and $P_{\mathrm{back}}>0$. The front is the short because that is the leg that cheapens when front yields rise. Choose a scale $\gamma$ so that gross dirty dollars equal $I$:

$$
\lvert P_{\mathrm{front}}\rvert + \lvert P_{\mathrm{back}}\rvert = I
$$

Gross $I$ is the budget knob; the DV01 identity is the shape. Small parallel $\Delta y$ then cancel to first order. After lot rounding, check residual DV01; do not assume the solved $P$ still match once face is an increment. Coupon bonds use

$$
P_c(t,T)=P(t,T)+k\delta\sum_{i=I(t)}^n P(t,T_i)
$$

with the usual Macaulay-to-modified conversion. This dirty-price identity is how $D$ is computed, not a second trading signal. Using clean prices in $P_{\mathrm{front}}$ while durations were computed on dirty prices will break the match.

### 4.4 Holding-period P&L

Price change plus coupon accrual minus financing:

$$
\mathrm{P\&L} = \Delta P_{\mathrm{front}} + \Delta P_{\mathrm{back}} + \mathrm{accrual} - \mathrm{repo} - \mathrm{costs}
$$

First-order check: duration P&L $\approx -\mathrm{DD}_{\mathrm{front}}\Delta y_f - \mathrm{DD}_{\mathrm{back}}\Delta y_b$. Report net return on gross $I$, Sharpe on **non-overlapping** holds, and residual DV01 after rounding. Repo each leg at its own rate. Specials on the short front of a flattener can dominate the slope P&L you thought you isolated.

## 5. Step-by-step algorithm

1. **Universe.** Same issuer, liquid benchmarks (e.g. 2s10s or 5s30s). Listed bond futures allowed if CTD is treated as the cash leg. This step exists so a credit-Treasury mix does not sneak in as “2s10s.” Futures without a CTD map are not a cash leg.
2. **Tenors.** Fix $(T_f,T_b)$. Pull dirty prices, yields, and modified durations as of $t < t_{\mathrm{fill}}$. Durations printed after $t$ (a late vendor run) do not belong in the $t$ match.
3. **Gate.** Flattener if the file’s rise-in-rates rule fires; steepener if the fall-in-rates rule fires; else flat or a mean-reversion fade of $s$. The gate is the only source of sign. A default always-flattener book is a different spec.
4. **Match.** Solve for $P_{\mathrm{front}}, P_{\mathrm{back}}$ with the DV01 identity and gross $I$. If the solve needs a long front on a flattener, the signs are wrong; stop and check $D$.
5. **Caps.** Clip each leg at a fraction of ADV or of issue size. After clipping, restore the DV01 match by scaling the other leg or by a residual cash bucket; do not drop one leg silently. A one-legged book is a duration bet.
6. **Blotter.** Convert to face value / contracts, round to the increment, emit intents. Do not route live orders. Rounding is why residual DV01 is a reported series, not an assumed zero.
7. **Roll.** If the front approaches a coupon, a CTD switch, or a tenor drift past a tolerance, roll to the new benchmark. Holding a 1.5-year “2-year” against a 10-year is not 2s10s.
8. **Rebalance.** Daily or when residual $\lvert\mathrm{DD}_{\mathrm{front}}+\mathrm{DD}_{\mathrm{back}}\rvert$ exceeds a tick-DV01 tolerance. Rebalancing every yield tick is turnover, not immunization of the match.

## 6. Execution protocol

- Default fill: next close after durations and yields are known. Delay-0 is research-only.
- Watch curve twist versus parallel: the identity only kills the parallel piece. A 2s30s twist on a 2s10s book is leftover risk, not a failed DV01 solver.
- Futures implementations must re-hedge on CTD switches. A conversion-factor jump is a discrete change in $D$ of the futures leg.
- Repo each leg at its own rate; specials on the short break the textbook carry. Using one GC rate on both legs will overstate flattener carry when the front is special.

## 7. Data contract

Required, point-in-time:

- Clean and dirty prices, accrued, yields
- Modified duration and DV01 on each leg
- Repo (or financing) per leg
- Issue identifiers and, if futures are used, conversion factors and CTD

Not used by this spec: equity book value, earnings, SUE, VIX, option chains, CDS (unless the two legs are credit bonds and you add a credit overlay in a different file).

No look-ahead on auctions, CTD, or revised durations after $t$. An auction that has not yet printed cannot be the $t$ front leg. A vendor duration restated next morning does not change the $t$ weights.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenors | 2s10s | 5s30s allowed |
| neutrality | DV01-neutral | not par-neutral |
| $I$ | caller-set | gross dirty dollars |
| rebalance | on DV01 drift | or daily |
| delay | 1 bar | delay-0 is research-only |
| issuer | same sovereign | mixing credits is a different trade |

## 9. Agent implementation contract

Build a Python module `strategies.yield_curve_flatteners_steepeners` with:

1. `spread(y_front, y_back) -> float` — $s=y_b-y_f$.
2. `dv01_weights(D_front, D_back, I, side) -> tuple` — $(P_{\mathrm{front}},P_{\mathrm{back}})$ with $P_{\mathrm{front}} D_{\mathrm{front}}=-P_{\mathrm{back}} D_{\mathrm{back}}$ and gross $I$ to `1e-8`.
3. `gate(signal) -> str` — `{flattener, steepener, flat}`.
4. `blotter(weights, prices, lot) -> list[OrderIntent]` — face/contracts, never live routing.
5. `pnl(dP, accrual, repo, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unmatched DV01.** Par-equal notionals leave a large level bet. If a parallel +10bp day dominates P&L, the match is broken.
- **Curvature.** A butterfly residual is not killed by two-leg duration match. 2s10s can lose on a 5s rally even with perfect DV01.
- **CTD switch.** Futures flatteners jump when the deliverable changes. Treating the future as a constant-duration 10-year is a failed spec.
- **Special repo.** The short front on a flattener can squeeze. Carry assumed at GC will not be the P&L.
- **Issuer mix.** A Treasury versus swap or Treasury versus credit is a spread product, not this curve file.
- **Gate look-ahead.** Labeling historical months as “hiking” using the full cycle is not a point-in-time signal.

## 11. Acceptance tests

- Parallel $\Delta y$ on both legs with the DV01 match → first-order P&L $=0$ to `1e-6` relative to $I$.
- Flattener signs: $P_{\mathrm{front}}<0$, $P_{\mathrm{back}}>0$. Steepener is the opposite.
- Gross $\lvert P_{\mathrm{front}}\rvert+\lvert P_{\mathrm{back}}\rvert=I$ to `1e-8`.
- Permuting yields after $t$ must not change the $t$ weights.
- After ADV clipping, either DV01 still matches or the cash bucket holds the residual; one leg is never dropped alone.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
