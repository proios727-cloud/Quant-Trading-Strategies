---
rank: 35
slug: rolling-down-the-yield-curve
title: "Rolling Down the Yield Curve"
asset_class: "fixed income"
style: "carry / roll-down harvest"
horizon: "Hold while the name sits on a steep sector; months"
instruments: "government and/or credit bonds; listed bond futures if used"
---

# 035. Rolling Down the Yield Curve

| Field | Value |
|---|---|
| Popularity rank (this kit) | 35 of 101 |
| Why it sits here | Classic if-the-curve-is-static income trade. Buy the steepest sector, hold as it rolls down, replace near maturity. |
| Aliases | roll-down, curve carry, riding the yield curve |
| Asset class | fixed income |
| Style | carry / roll-down harvest |
| Typical horizon | Hold while the name sits on a steep sector; months |
| Instruments | government and/or credit bonds; listed bond futures if used |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

If the yield curve is unchanged, a bond’s yield falls as its remaining maturity shortens whenever the local slope is positive. That price gain is roll-down. Own the sector where roll-down is largest, hold as the name slides down the curve, and replace it as it approaches the short end.

This is a long-only income trade. It is not duration-neutral. A parallel selloff dominates roll-down. You are not flattening 2s10s (file 033) and you are not immunizing a liability (file 034). You are choosing a tenor because its static-curve carry looks high, and you are warehousing that tenor’s DV01.

Typical users are FI income sleeves and insurance books that can hold government duration. Horizon is months while the name sits on a steep sector, then a recycle into the then-steepest bucket. Monthly scans are enough; daily rebalancing $C_{\mathrm{roll}}$ is noise in the duration. Delay-1 fills are the research default.

Credit is allowed only if you accept spread roll-down as a different risk. A steep credit curve can be a distress signal, not a gift.

## 2. First principles

Write a zero’s continuously compounded yield as $R(t,T)=-\ln P(t,T)/(T-t)$. Over a short horizon $\Delta t$, the holding return splits into the yield earned plus a price change from the remaining maturity shrinking. If the **term structure is frozen**, $R(t,T)=f(T-t)$ for a fixed shape $f$, that price change is roll-down.

Carry over $[t,t+\Delta t]$ on a zero maturing at $T$ is

$$
C(t,t+\Delta t,T) = R(t,T)\,\Delta t + C_{\mathrm{roll}}(t,t+\Delta t,T)
$$

The first term is income from sitting at yield $R$. The second is the price gain (or loss) from sliding along a static shape. If you skip the split and rank on yield alone, you will prefer the longest bond on an upward curve even when the steep sector is in the belly. Realized return is not $C$: $C$ is the forecast under a frozen curve.

The roll-down piece is the duration times the yield change implied by sliding along a static curve:

$$
C_{\mathrm{roll}} \approx -\mathrm{ModD}(t,T)\bigl[R(t,T-\Delta t)-R(t,T)\bigr]
$$

Evaluate $R(t,T-\Delta t)$ on today’s curve at a shorter tenor, not on next month’s print. On an upward-sloping curve, $R(t,T-\Delta t)<R(t,T)$, so $C_{\mathrm{roll}}>0$: the bond “rolls down” to a lower yield and the price rises. On an inverted sector the sign flips and this spec skips or underweights. Pick the tenor $T$ that maximises $C_{\mathrm{roll}}$ (the steepest sector). Sell as remaining maturity nears the short end, where slope and duration both shrink, and recycle into the then-steepest sector.

That is the whole strategy. Everything below is how to measure $C_{\mathrm{roll}}$ on coupon bonds, how to scan buckets, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t,T)$ | zero price |
| $R(t,T)=-\ln P(t,T)/(T-t)$ | continuously compounded yield |
| $P_c(t,T)$ | coupon-bond dirty price |
| $\mathrm{ModD}(t,T)$ | modified duration |
| $\mathrm{DD}=\mathrm{ModD}\cdot P_c$ | dollar duration |
| $C(t,t+\Delta t,T)$ | total carry over $\Delta t$ under a frozen curve |
| $C_{\mathrm{roll}}$ | roll-down component of carry |
| $\Delta t$ | horizon used to measure roll-down (default 1 month) |
| $w_i$ | long-only weights, $\sum_i w_i=1$ |
| $I$ | dollars invested |

## 4. Mathematics

### 4.1 Frozen-curve carry

For zeros, constant term structure $R(t,T)=f(T-t)$:

$$
C(t,t+\Delta t,T) = R(t,T)\,\Delta t + C_{\mathrm{roll}}(t,t+\Delta t,T)
$$

The first term is the yield income. The second is roll-down. If the curve is flat, $C_{\mathrm{roll}}=0$ and carry collapses to $R\Delta t$. Coupon bonds replace $R$ and $\mathrm{ModD}$ with the bond’s yield and modified duration, using

$$
P_c(t,T)=P(t,T)+k\delta\sum_{i=I(t)}^n P(t,T_i)
$$

Dirty price and the coupon strip are how you get a bond yield and duration that are comparable across buckets. Ranking on quoted clean prices without duration is not roll-down.

### 4.2 Roll-down

$$
C_{\mathrm{roll}} \approx -\mathrm{ModD}(t,T)\bigl[R(t,T-\Delta t)-R(t,T)\bigr]
$$

Evaluate $R(t,T-\Delta t)$ on the **same** date-$t$ curve, not on a future curve. That is the static-shape identity. Using $R(t+\Delta t,T)$ would be next month’s return, which is look-ahead, not carry. Sign:

- steep positive sector → $C_{\mathrm{roll}}>0$ → **long** that tenor
- inverted / flat sector → $C_{\mathrm{roll}}\le 0$ → skip or underweight

A large $\mathrm{ModD}$ with a tiny slope can still beat a steep short-end sector. That is why you maximise $C_{\mathrm{roll}}$, not slope alone and not duration alone.

### 4.3 Sector scan

Bucket liquid governments by remaining maturity (e.g. 2y, 5y, 7y, 10y, 20y, 30y). In each bucket compute $C_{\mathrm{roll}}$ on the on-the-run (or a fitted par rate). Allocate $I$ long-only to the bucket that maximises $C_{\mathrm{roll}}$, or spread across the top $k$ buckets. Not a curve-neutral book: net DV01 is that of the chosen sector. If you short the long end against the roll-down long, you have built a flattener (file 033), not this trade.

### 4.4 Holding-period P&L

Realized P&L is price change plus coupon accrual minus financing, whether or not the curve stayed put:

$$
\mathrm{P\&L} = \Delta P_c + \mathrm{accrual} - \mathrm{repo} - \mathrm{costs}
$$

Duration P&L $\approx -\mathrm{DD}\,\Delta y$ will dominate $C_{\mathrm{roll}}$ whenever yields sell off. Report return on $I$, an attribution into yield + roll-down + curve surprise, and one-way turnover. If the attribution is missing, a lucky bull market will be mistaken for roll-down skill.

## 5. Step-by-step algorithm

1. **Universe.** Liquid government bonds (default). Credit allowed only if you accept spread roll-down as a different risk. This step exists so an agent does not silently fill the scan with high-yield names whose “roll-down” is a credit-spread compression bet.
2. **Curve.** Fit or take par/zero yields dated $\le t$. Do not use a curve published after $t_{\mathrm{fill}}$. A restated history of fitted zeros is look-ahead if those zeros were not available at $t$.
3. **Scan.** For each tenor bucket, compute $C_{\mathrm{roll}}$ with $\Delta t=1$ month and the bucket’s $\mathrm{ModD}$. Missing $R(t,T-\Delta t)$ on the short end of a bucket means drop that bucket, not interpolate from next month.
4. **Pick.** Long the maximising bucket (or top $k$). Skip inverted buckets unless the mandate allows shorts. The pick is the only alpha step; everything else is risk and plumbing.
5. **Size.** $w_i\ge 0$, $\sum w_i=1$, dollars $D_i=w_i I$. Cap by issue size / ADV. This is long-only on purpose. A short tail would be a curve-neutral carry factor (closer to file 057).
6. **Blotter.** Convert to face, round, emit intents. Do not route live orders. Prefer on-the-run or the cheapest liquid off-the-run in the winning bucket.
7. **Exit.** Sell when remaining maturity hits a short-end cutoff, when local slope flattens below a threshold, or when a duration budget is hit. Recycle into the then-steepest sector. Holding into 3-month bills because last quarter’s scan liked 2s is not the rule.
8. **Rebalance.** Monthly scan. Delay-1: this month’s $C_{\mathrm{roll}}$ trades the next close. Daily scans will churn duration without changing the steep-sector view.

## 6. Execution protocol

- Default fill: next close after the scan. Delay-0 is research-only.
- Prefer on-the-run or cheapest liquid off-the-run in the winning bucket; do not chase stale quotes. A screen yield on a bond that has not traded is not $C_{\mathrm{roll}}$ you can harvest.
- Exit when the local slope flattens or the duration budget is hit.
- This is not a flattener: do not short the long end against the roll-down long.

## 7. Data contract

Required, point-in-time:

- Clean/dirty prices, accrued, yields, modified duration
- A dated yield curve (zeros or pars) for $R(t,T)$ and $R(t,T-\Delta t)$
- Repo or financing if P&L is excess return
- Issue size / ADV for caps

Not used by this spec: equity book value, earnings, SUE, VIX, option chains, COT, CDS.

No look-ahead on future curves. $R(t,T-\Delta t)$ is read from today’s curve at a shorter tenor, not from next month’s print. If the agent implements $C_{\mathrm{roll}}$ as next month’s observed price change, the test in Section 11 must fail.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $\Delta t$ | 1 month | roll-down horizon |
| universe | liquid governments | |
| allocation | max $C_{\mathrm{roll}}$ bucket | top-$k$ allowed |
| short-end cutoff | remaining maturity below 1y | recycle |
| long-only | on | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.rolling_down_the_yield_curve` with:

1. `carry(R, ModD, dt) -> dict` — $C$ and $C_{\mathrm{roll}}$ from Section 4.1–4.2, using the date-$t$ curve only.
2. `scan(curve, buckets, dt) -> pd.Series` — $C_{\mathrm{roll}}$ by tenor, no look-ahead.
3. `weights(scan, I, k) -> pd.Series` — long-only, $\sum w_i=1$ to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — face amounts, never live routing.
5. `pnl(dP, accrual, repo, costs) -> float` — matches the P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Bear steepener / parallel selloff.** Duration P&L swamps $C_{\mathrm{roll}}$. The identity never said the curve would stay put.
- **Curve inversion.** Roll-down flips sign; a static long in the old steep sector loses. The monthly scan is what cuts that; skipping the scan to “let it ride” is a different spec.
- **Off-the-run liquidity.** Cheap roll-down on a stale bond is not tradable at the screen. Caps exist because of this, not as decoration.
- **Credit.** Spreads can steepen while the Treasury curve is static. A credit universe then attributes spread P&L to roll-down.
- **Look-ahead curve.** Building $C_{\mathrm{roll}}$ from $R(t+\Delta t,\cdot)$ is next month’s return labeled as carry.
- **Hidden flattener.** Shorting another tenor to “reduce duration” converts the book into file 033.

## 11. Acceptance tests

- Flat curve: $R(t,T-\Delta t)=R(t,T)$ → $C_{\mathrm{roll}}=0$ to `1e-8`.
- Upward-sloping toy zeros: $C_{\mathrm{roll}}>0$ and $C=R\Delta t+C_{\mathrm{roll}}$.
- $C_{\mathrm{roll}}$ at $t$ is invariant to permuting the curve after $t$.
- Weights are long-only and sum to 1.
- Adding linear costs $\tau$ weakly decreases P&L.
- Using the next month’s observed yield in place of $R(t,T-\Delta t)$ must not be accepted as `carry`.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
