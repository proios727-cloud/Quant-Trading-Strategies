---
rank: 6
slug: fx-carry
title: "FX Carry Trade"
asset_class: "foreign exchange"
style: "carry / long high-yield currency"
horizon: "1–12 months; typical academic holding 1 month"
instruments: "FX spot; FX forwards (typically 1m); G10 and liquid EM pairs"
---

# 006. FX Carry Trade

| Field | Value |
|---|---|
| Popularity rank (this kit) | 6 of 101 |
| Why it sits here | The textbook FX premium trade. Borrow low-rate, invest high-rate, leave FX unhedged. Among the most studied anomalies in international finance. |
| Aliases | uncovered interest carry, forward-premium trade |
| Asset class | foreign exchange |
| Style | carry / long high-yield currency |
| Typical horizon | 1–12 months; typical academic holding 1 month |
| Instruments | FX spot; FX forwards (typically 1m); G10 and liquid EM pairs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Covered interest prices the forward from the two interest rates. Uncovered interest says the high-rate currency should depreciate by that same gap. Empirically the depreciation often fails to show up, so selling the expensive forward (buying the discount) earns the interest differential.

You are betting that the interest gap arrives as cash while the spot move over the holding window is smaller, in magnitude, than that gap. The economic picture is simple: borrow the low-yield currency, lend the high-yield currency, and leave the FX unhedged. The traded instrument is usually a forward, which is the same cash-plus-swap package in one line.

You are not betting that covered interest is broken. Covered interest is the pricing identity that tells you what the forward *should* be. You are also not betting that you can collect a CIP basis as free P&L, and you are not ranking currencies against each other in a high-minus-low book — that sibling is `027`. A single-pair carry book can be long one high-yield name versus the domestic numeraire; a basket just repeats the same sign rule.

Typical users are FX overlay desks, CTA carry sleeves, and academic replications of the forward-premium puzzle. The academic hold is one month on a 1m forward. Practitioners stretch to 3–12 months, but the identity does not get safer just because the tenor is longer: crash risk and EM convertibility still sit in the unhedged spot.

Horizon intuition: carry accrues slowly; crashes arrive in a few days. A month of collected differential can vanish in one funding-currency rally. Size so that a 3–4σ FX shock does not breach the risk limit, then rebalance on the fixing calendar, not on a discretionary “this pair still looks cheap.”

## 2. First principles

Quote spot $S(t)$ as units of domestic per one unit of foreign. A cash-and-carry that is long foreign, financed in domestic, and fully FX-hedged with a forward must earn zero in frictionless markets. That no-arbitrage statement is covered interest (CIRP). It pins the forward:

$$
F(t,T) = S(t)\,\frac{1+r_d}{1+r_f}
$$

This is not a forecast. It is the price that makes a fully hedged loan in foreign, financed in domestic, earn nothing after you lock the FX with $F$. If the traded forward sits away from this CIRP value, the gap is a *basis* you pay or receive, not “extra carry.” Mixing CIRP residual into tradable P&L is how a CIP-stress month gets booked as alpha.

Uncovered interest (UIRP) drops the hedge and replaces the known forward with the expected future spot:

$$
(1+r_d) = \frac{\mathbb{E}_t[S(t+T)]}{S(t)}\,(1+r_f)
$$

If UIRP held, the high-$r_f$ currency would be expected to depreciate just enough to cancel the yield gap, and there would be no average profit to holding it unhedged. The left side is what you earn staying in domestic. The right side is what you earn, in expectation, if you convert to foreign, earn $r_f$, and convert back at the future spot. Equality is the “no average profit” statement.

Carry is the empirical failure of that offset: $\mathbb{E}_t[S(t+T)]$ does not track $F(t,T)$. The log forward discount is the interest gap, up to day-count:

$$
D(t,T) = \ln S(t) - \ln F(t,T) \approx r_f - r_d
$$

$D>0$ means the foreign currency is at a forward discount: $F<S$, high $r_f$. Buying the forward (long foreign) then earns carry if spot does not fall by the full CIRP amount. $D<0$ is a premium: you sell the forward (short the low-yield foreign). Rank or sign on $D$ computed from quotes you already have. Never on a future spot, and never on a revised fixing that printed after the decision.

That is the whole strategy. Everything below is how to read $D$ from the tape, how to turn it into a basket, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S(t)$ | spot FX, units of domestic per 1 unit of foreign |
| $F(t,T)$ | outright forward to tenor $T$ |
| $r_d, r_f$ | domestic and foreign risk-free simple rates over $T$ |
| $D(t,T)$ | forward discount $\ln S(t)-\ln F(t,T)$ |
| $i=1,\ldots,N$ | currencies (or pairs vs the domestic numeraire) |
| $w_i$ | signed weight on currency $i$; $w_i>0$ is long foreign |
| $N_{\mathrm{fx}}$ | foreign-currency notional of a long forward |
| $I$ | gross notional, $I=\sum_i \lvert w_i\rvert$ in domestic units of the book |

A long foreign forward settles in domestic on the FX difference versus $F(t,T)$. It is economically the unhedged high-yield loan.

## 4. Mathematics

### 4.1 Signal

From CIRP, $D(t,T)\approx r_f-r_d$. Rank or sign on $D$, never on a future spot. The sign is the entire timer for a one-pair book; the basket just repeats it.

Sign rule for one pair:

- $F<S$ (discount, $D>0$) — **buy** the forward: long high-yield foreign
- $F>S$ (premium, $D<0$) — **sell** the forward: short low-yield foreign
- $F=S$ — flat

If you invert the quote convention (foreign per domestic instead of domestic per foreign), $D$ flips sign. Pick one convention in the data contract and convert once. Mixing conventions inside a basket is a silent long-short bug, not a diversification overlay.

### 4.2 Basket weights

Equal-weight or inverse-vol a basket of high-yield names versus a basket of low-yield names. For a signed book with target gross $I$,

$$
w_i = \gamma\,\mathrm{sign}(D_i)
$$

Every name with a positive discount gets the same absolute weight, every name with a negative discount the opposite. $\gamma$ is not a forecast; it is the scalar that will be rebuilt so the gross identity holds. Names with $D_i=0$ are flat. This scheme ignores volatility, so a noisy EM pair can dominate a quiet G10 pair in risk even when notionals match.

or, with a vol target,

$$
w_i = \gamma\,\frac{\mathrm{sign}(D_i)}{\sigma_i}
$$

$\sigma_i$ is realized FX vol on a window that **ends before** the fill (default 60 daily bars). Inverse-vol is how you stop the noisy metal-analogue of FX — a high-vol EM name — from eating the risk budget. If $\sigma_i$ is missing, drop the name; do not impute $\sigma_i=0$, which would send $\lvert w_i\rvert$ to infinity.

Choose $\gamma$ so that

$$
\sum_i \lvert w_i\rvert = 1
$$

This is the gross-one identity. After any drop, clip, or dead-band, rebuild $\gamma$ on the remainder. Keeping the old $\gamma$ after a name disappears silently inflates (or deflates) every other weight and breaks tests that check the sum to `1e-8`.

Optional: drop names with $\lvert D_i\rvert$ below a dead-band so near-zero differentials do not flip every month. The dead-band is a turnover control, not a second signal. Document it; toggling it on and off inside a backtest is a different book each time.

### 4.3 Forward excess return

A long foreign notional of 1, entered at $F(t,T)$ and marked at $S(t+T)$, pays the domestic increment

$$
RX_{t\to t+T} = \frac{S(t+T)-F(t,T)}{S(t)}
$$

The division by $S(t)$ puts the P&L in domestic return units on the foreign notional. If spot is unchanged, $RX \approx D > 0$ on the high-yield leg. That is the carry. Spot moves are the unhedged FX risk. If you mark at mid and trade at bid/ask, the backtest overstates $RX$ by about half the spread on each entry and exit.

### 4.4 Holding-period P&L

For notionals $N_{\mathrm{fx},i}$ in foreign currency $i$,

$$
\mathrm{P\&L} = \sum_i N_{\mathrm{fx},i}\bigl(S_i(t+T)-F_i(t,T)\bigr) - \mathrm{costs}
$$

This is the cash settlement of the forwards in domestic currency, minus whatever you put in the cost term: spread, roll, and CIP/funding if you trade the actual market forward rather than the CIRP ghost. Cash-plus-swap implementations earn the same thing: interest differential plus unhedged $\Delta S$. Do not add the CIRP residual a second time on top of this identity.

Report:

- net return on gross $I$
- annualized Sharpe on **non-overlapping** holding-period returns
- one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

The one-half is the usual one-way convention: a full flip of the book is turnover $1$, not $2$. Overlapping a 3-month hold as three stacked 1-month books inflates Sharpe if you annualize the overlapping series. Use non-overlapping holds.

Implement the CIRP residual $F-S(1+r_d)/(1+r_f)$ as a **diagnostic**, never as a free lunch. CIP basis and funding have to be in the cost term. If you do $X$ = treat a non-zero CIP residual as tradable alpha, the backtest lies: that residual is often a balance-sheet price you cannot warehouse at the paper mid.

## 5. Step-by-step algorithm

1. **Universe.** G10, optionally liquid EM. Drop pegs, convertibility traps, and names without a deliverable or NDF forward. Keep only pairs with a published fixing calendar. This step exists because a peg with a high policy rate looks like infinite carry until the peg breaks; convertibility traps look like a rate you cannot actually earn.
2. **Tenor.** Default $T=$ 1 month. Read $S(t)$ and $F(t,T)$ from timestamps strictly before the fill. This step exists so the signal and the instrument share a tenor. Mixing a 1m $D$ with a 12m forward is a curve trade, not this spec.
3. **Discount.** Compute $D_i(t,T)=\ln S_i(t)-\ln F_i(t,T)$. If outright forwards are missing, build them from spot plus forward points, still delay-1. This step exists because points and outrights are two encodings of the same $F$; mixing a live outright with stale points is look-ahead or look-behind, both of which lie.
4. **Score.** Sign, rank, or inverse-vol as in §4.2. Dead-band optional. This step exists to turn a signed discount into a portfolio. Skipping it and holding “the highest $D$ name at 100%” is a different, more concentrated book.
5. **Size.** Scale to gross $I$, or to an annualized vol target (default off; 10% if on). Cap so a $3$–$4\sigma$ FX shock does not breach the caller’s risk limit. This step exists because equal notionals are not equal risk; EM vol can be several times G10 vol.
6. **Instrument.** Enter via outright forwards, or via cash plus FX swap. Do not mix the two in one blotter line. This step exists so P&L has one settlement identity. Mixing them double-counts carry or drops it.
7. **Blotter.** Emit intents. Do not route live orders. This step exists because the spec is a research book; live routing is out of scope and refused in the agent contract.
8. **Roll.** Rebalance monthly on the fixing calendar. A 1m book that is not closed is rolled, not held through a second fixing without a new $D$. This step exists because a stale $D$ from last month is not this month’s interest gap.

## 6. Execution protocol

- Default fill: next fixing / next London 16:00 WM after $D$ is known. Delay-0 same-fixing trades are research-only. If you fill at the same WM print that produced $D$, the backtest lies: that print was not tradable after you saw it.
- Size from traded-outright spreads, not mids. EM forward points can wipe the premium. If you do $X$ = use mid $F$ as the fill, the backtest lies by about the half-spread each way.
- If a name cannot be borrowed or the NDF is too wide, drop it and rebuild $\gamma$ on the remainder. Do not keep the high-yield longs and skip the funding shorts. That silent one-legged book is a dollar bet, not carry.

## 7. Data contract

Required, point-in-time:

- Spot mid and bid/ask
- Outright forwards or spot plus forward points, same timestamp convention
- Overnight and tenor money-market rates for the CIRP diagnostic
- Fixing calendar, holiday gaps, and settlement lag (T+1 / T+2)
- Bid/ask on the forward, or a conservative spread model

Not used by this spec: equity book values, earnings, futures COT.

No restatement of past fixings. A revised WM print after $t$ does not change the $t$ decision. If you do $X$ = rebuild $D_t$ after a WM restatement, the backtest lies. If you do $X$ = use a Friday close as Monday’s $D$ across a holiday gap without the actual fixing, the backtest lies. Delisted or halted pairs stay out; do not stitch a proxy cross and call it the same $D$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor $T$ | 1 month | academic holding; 3–12m allowed |
| universe | G10 | liquid EM optional |
| rebalance | monthly | on the fixing calendar |
| weighting | equal or $1/\sigma$ | $\sigma$ from 60d daily FX |
| vol target | off | 10% ann. if on |
| dead-band on $\lvert D\rvert$ | off | stops noise flips |
| delay | 1 fixing | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.fx_carry` with:

1. `discount(spot, forward) -> pd.Series` — $D_i=\ln S_i-\ln F_i$, no look-ahead.
2. `weights(discount, I, vol=None) -> pd.Series` — $w_i$ with $\sum \lvert w_i\rvert=1$ to `1e-8`.
3. `blotter(weights, forwards, I) -> list[OrderIntent]` — forward notionals, never live routing.
4. `pnl(notionals, spot_T, forward_entry, costs) -> float` — matches $\sum N_i(S_i(T)-F_i)-\mathrm{costs}$.
5. `cip_residual(spot, forward, r_d, r_f) -> pd.Series` — diagnostic only.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Carry crash.** The funding currency rips higher; high-yield names gap down together. The identity still says you were long the high-$D$ names; it does not say those names cannot all sell off.
- **CIP / funding stress.** The traded forward is not the CIRP forward; the “carry” is a basis you pay. Treating CIP residual as alpha is the lie.
- **Convertibility and weekend gaps.** EM names gap over holidays; NDF fixing risk is not the same as G10 delivery.
- **Costs.** Transaction costs on EM forwards can exceed the interest gap. A paper $D$ of 8% annualized with 4% round-trip points is not 8% expected return.

## 11. Acceptance tests

- CIRP toy: $F=S(1+r_d)/(1+r_f)$ implies $D\approx r_f-r_d$ to $10^{-8}$ in logs of one-period rates.
- Two names with $D=+x$ and $D=-x$, equal $\sigma$ → equal-magnitude opposite weights, $\sum \lvert w_i\rvert=1$.
- Permuting spots and forwards after the decision timestamp must not change $D_t$ or $w_t$. If it does, the implementation looked ahead.
- A path with $S(t+T)=S(t)$ pays approximately the interest differential on the long high-yield notional, minus costs.
- Adding linear costs $\tau$ weakly decreases P&L.
- CIP residual is returned and **not** added to tradable P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
