---
rank: 57
slug: bond-carry-factor
title: "Bond Carry Factor"
asset_class: "fixed income"
style: "cross-sectional carry"
horizon: "Monthly cross-section"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 057. Bond Carry Factor

| Field | Value |
|---|---|
| Popularity rank (this kit) | 57 of 101 |
| Why it sits here | Koijen–Moskowitz–Pedersen–Vrugt style bond carry. Cross-section of roll-down plus yield. |
| Aliases | bond carry, KMPV carry |
| Asset class | fixed income |
| Style | cross-sectional carry |
| Typical horizon | Monthly cross-section |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Rank bonds on total carry: the return if the yield curve is unchanged over the next month (yield income plus roll-down). Long the top decile, short the bottom, zero cost. Optional: duration-neutral inside maturity buckets so the book is not just long duration.

You are betting that high frozen-curve $C$ outperforms low $C$ as compensation for duration, credit, and inversion risk. You are not immunizing a liability (file 034) and you are not only picking the steepest long-only sector (file 035). File 035 is long-only roll-down; this file is a cross-sectional long/short on total carry. File 058 is a spread residual versus ratings; this file does not use ratings as the signal.

Typical users are FI factor books. Horizon is monthly. $C$ is the signal, not the realized return. Using next month’s observed price in $C$ is look-ahead: that is next month’s return labeled as carry. Delay-1: month-$t$ carry trades the next close.

## 2. First principles

The one-period return of a zero from $t$ to $t+\Delta t$, if you could mark it on a curve that has not yet moved, is the price change along a frozen term structure:

$$
C(t,t+\Delta t,T)=\frac{P(t+\Delta t,T)-P(t,T)}{P(t,T)}
$$

Here $P(t+\Delta t,T)$ is **not** next month’s observed price. It is today’s zero curve, read at the shorter remaining maturity $T-(t+\Delta t)$ versus $T-t$. If an implementer plugs in the future price, every look-ahead test must fail. Under that frozen curve the same carry splits as yield plus roll-down:

$$
C = R\,\Delta t + C_{\mathrm{roll}}
$$

with $R(t,T)=-\ln P(t,T)/(T-t)$ and $C_{\mathrm{roll}}$ as in the roll-down spec. The split is diagnostic: ranking on $C$ already includes both pieces. Financed books replace $R$ by $R-r_f$; that shift is rank-invariant if $r_f$ is common. If financing differs by name (specials, haircuts), excess carry is not rank-invariant and must be computed name by name.

Cross-sectional carry says high-$C$ bonds outperform low-$C$ bonds on average, as compensation for the duration, credit, and inversion risks that produce high $C$. Long top decile, short bottom.

That is the whole factor. Everything below is the sort, optional duration buckets, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t,T)$ | zero price |
| $R(t,T)=-\ln P(t,T)/(T-t)$ | continuously compounded yield |
| $P_c$ | coupon-bond dirty price |
| $\mathrm{ModD}$, $\mathrm{DD}$ | modified and dollar duration |
| $C(t,t+\Delta t,T)$ | frozen-curve carry |
| $C_{\mathrm{roll}}$ | roll-down piece |
| $r_f$ | financing rate |
| $w_i$ | signed weights, $\sum_i w_i=0$, $\sum_i\lvert w_i\rvert=1$ |
| $I$ | gross dirty dollars |
| $D_i=w_i I$ | signed holdings |

## 4. Mathematics

### 4.1 Carry

On each bond, using the date-$t$ curve only:

$$
C(t,t+\Delta t,T)=\frac{P(t+\Delta t,T)-P(t,T)}{P(t,T)}
$$

$P(t+\Delta t,T)$ is the frozen-curve mark. Coupon bonds use dirty prices and the same slide of remaining maturity. Default $\Delta t=1$ month. A bond that matures inside $\Delta t$ does not have a well-defined frozen mark at $T$; drop it.

Under a frozen curve, $C = R\Delta t + C_{\mathrm{roll}}$ with $C_{\mathrm{roll}}$ from modified duration times the slide in yield. Financed books replace $R$ by $R-r_f$ (rank-invariant if $r_f$ is the same for every name).

### 4.2 Cross-section

Long top decile of $C$, short bottom decile. Equal-weight inside tails, then

$$
\sum_i w_i = 0, \qquad \sum_i \lvert w_i\rvert = 1
$$

Without duration buckets this book is often long duration on the high-$C$ tail. That may be acceptable as “carry is compensation,” but it is not a pure curve-shape bet. Optional duration-neutral variant: sort inside maturity buckets, long/short within bucket, so net DV01 per bucket is near zero.

### 4.3 Holding-period P&L

Realized return is not $C$; $C$ is the signal. P&L is price change plus coupon minus financing minus costs:

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Duration P&L $\approx -\mathrm{DD}\,\Delta y$ is the main surprise versus $C$. Report return on $I$, Sharpe on **non-overlapping** months, and an attribution into carry versus curve surprise. If attribution is missing, a bull market in duration will be mistaken for a carry factor.

## 5. Step-by-step algorithm

1. **Universe.** Liquid governments and/or credits. Constant-maturity yields or matched bonds. Keep called/matured names until the event date. This step exists so survivorship does not drop the defaulted cheap tail after the fact.
2. **Curve.** Point-in-time zeros or pars dated $\le t$. A curve published after $t_{\mathrm{fill}}$ cannot mark $P(t+\Delta t,T)$.
3. **Carry.** Compute $C$ with $\Delta t=1$ month on the frozen curve. Drop missing $C$. Do not substitute next month’s dirty price.
4. **Sort.** Deciles of $C$. Long top, short bottom. Equal-weight inside tails unless a documented scheme says otherwise.
5. **Optional buckets.** Repeat the sort inside duration buckets and duration-hedge each bucket. Turn this on if you need to claim the factor is not just duration.
6. **Weights.** Dollar-neutral, gross $I$. Cap by issue size / ADV. Restore neutrality after caps.
7. **Blotter.** Face amounts, round, emit intents. Do not route live orders. Repo the short tail; specials break financed carry.
8. **Rebalance.** Monthly. Delay-1: month-$t$ carry trades the next close. Daily carry resorts will churn duration for no new information.

## 6. Execution protocol

- Default fill: next close after $C$ is known. Delay-0 is research-only.
- Use constant-maturity yields or matched bonds; do not mix a 30-year off-the-run with a 2-year on-the-run without a duration bucket.
- Repo the short tail; specials break financed carry.

## 7. Data contract

Required, point-in-time:

- Clean/dirty prices, yields, durations
- Dated zero or par curve for the frozen mark $P(t+\Delta t,T)$
- Repo / $r_f$ if P&L is excess
- Ratings only if the universe is credit (filter, not the signal)

Not used by this spec: the ratings-and-maturity residual of 058, CDS basis, equity book value, earnings, SUE.

No look-ahead: $P(t+\Delta t,T)$ is not the future price. A test that builds $C$ from the observed $t+\Delta t$ dirty price must fail.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $\Delta t$ | 1 month | |
| sort | deciles | |
| duration buckets | off | on → DV01-neutral inside buckets |
| rebalance | monthly | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bond_carry_factor` with:

1. `carry(curve, bond, dt) -> float` — $C$ from the frozen curve, no look-ahead.
2. `weights(C, I, buckets=None) -> pd.Series` — $\sum w_i=0$, $\sum\lvert w_i\rvert=1$ to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — face, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}}-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Carry is compensation.** High $C$ is often high duration or high credit. A parallel selloff will hit the long tail first.
- **Crowding.** The same curve is public. Capacity is issue size, not the smoothness of $C$.
- **Curve inversion.** Rankings flip; a sticky long-duration tail loses. Monthly resort is what updates that.
- **Looking ahead.** Using next month’s price in $C$ is not carry; it is next month’s return.
- **Specials.** Name-specific repo means financed $R-r_f$ is not a common shift and ranks change.
- **Mixing 058.** Residualizing $C$ by rating is a different factor; do not do it silently.

## 11. Acceptance tests

- Frozen flat curve: $C=R\Delta t$ (zeros) to `1e-6`.
- $C$ at $t$ is invariant to permuting the curve after $t$.
- Decile toy: highest $C$ is long, lowest $C$ is short, $\sum w_i=0$, $\sum\lvert w_i\rvert=1$.
- Financed $R-r_f$ does not change ranks if $r_f$ is common.
- Adding linear costs $\tau$ weakly decreases P&L.
- Substituting the observed future dirty price for the frozen mark must not be accepted as `carry`.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
