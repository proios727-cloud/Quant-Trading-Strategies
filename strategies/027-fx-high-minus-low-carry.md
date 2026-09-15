---
rank: 27
slug: fx-high-minus-low-carry
title: "High-Minus-Low FX Carry"
asset_class: "foreign exchange"
style: "cross-sectional carry / dollar-neutral"
horizon: "Monthly rebalance"
instruments: "FX spot; FX forwards (typically 1m); G10 and liquid EM pairs"
---

# 027. High-Minus-Low FX Carry

| Field | Value |
|---|---|
| Popularity rank (this kit) | 27 of 101 |
| Why it sits here | The Lustig–Roussanov–Verdelhan HML-FX factor. Cross-sectional version of carry; standard in currency risk-premia research. |
| Aliases | HML-FX, cross-sectional carry |
| Asset class | foreign exchange |
| Style | cross-sectional carry / dollar-neutral |
| Typical horizon | Monthly rebalance |
| Instruments | FX spot; FX forwards (typically 1m); G10 and liquid EM pairs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Rank currencies by forward discount $D_i(t,T)$. Buy the top quantile, sell the bottom quantile. Structure the two legs so the book is dollar-neutral.

You are betting that high-discount currencies outperform low-discount currencies over the next month, in excess-return space, after cancelling the common dollar rate that sits in every $D_i$ versus USD. Covered interest still prices each forward. Uncovered interest still fails in the cross-section: the depreciation does not fully offset the rank of $D$.

You are not running single-pair or equal-sign dollar carry (`006`, `053`). Those books can be net long every foreign name at once. You are not collecting CIP basis as alpha. You are not ranking on past spot returns (that is FX trend, `052`). The HML construction exists specifically because a long-only high-$D$ book is still a bet on foreign rates versus the dollar.

Typical users are currency-risk-premia researchers and FX overlay desks that want a dollar-neutral carry factor. Universe is G10 ex-USD, optionally liquid EM, all quoted versus the same numeraire. Horizon is monthly on 1m forwards. Thirds of G10 are about three names per leg: concentration is the design, not an accident.

If the short leg is missing (no borrow, no NDF), HML collapses to dollar carry. Rebuild both legs or refuse the book. Delay-1 on the fixing calendar.

## 2. First principles

Covered interest still prices each forward:

$$
F_i(t,T) = S_i(t)\,\frac{1+r_d}{1+r_{f,i}}
$$

Same identity as in `006`, now with a foreign rate indexed by $i$. The forward is not a forecast of $S_i(t+T)$; it is the CIRP price. A traded forward away from this value is CIP basis, tracked as a diagnostic, not added to HML P&L.

The log discount is the foreign-minus-domestic rate gap:

$$
D_i(t,T) = \ln S_i(t) - \ln F_i(t,T) \approx r_{f,i} - r_d
$$

Every $D_i$ contains $-r_d$. If all quotes are versus USD, that common piece is the dollar rate. Sorting on $D_i$ still ranks foreign rates, but a long-only book on high $D$ keeps the dollar as a residual factor. $D$ is read from spot and forward timestamps strictly before the fill. A revised WM print after $t$ does not change $D_t$.

UIRP says high-$D_i$ currencies depreciate enough to cancel $D_i$. Cross-sectional carry is the claim that they do not: sorting on $D_i$ predicts next-period excess returns with the **same** sign as $D_i$. Because every $D_i$ contains $-r_d$, a long-only high-$D$ book is still a bet on foreign rates versus the dollar. High-minus-low cancels that common piece:

$$
D_i - D_j \approx r_{f,i} - r_{f,j}
$$

The dollar rate drops out of the *difference* of discounts. Long the top quantile of $D$, short the bottom quantile, and the sort key no longer embeds $-r_d$. The book can then be forced to $\sum w_i=0$. Adding a constant to every $D_i$ must not change ranks — that is the test that the common dollar piece cancelled.

That is the whole strategy. Everything below is quantiles, weights, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i=1,\ldots,N$ | currencies quoted vs the domestic numeraire (USD in the LRV construction) |
| $S_i(t), F_i(t,T)$ | spot and forward, domestic per 1 foreign |
| $D_i(t,T)$ | forward discount |
| $Q_H, Q_L$ | high and low quantiles of $D_i$ |
| $w_i$ | signed weight; $w_i>0$ long foreign $i$ |
| $\sigma_i$ | FX vol for inverse-vol weights |
| $I$ | gross notional |

Dollar-neutral means $\sum_i w_i=0$ and $\sum_i \lvert w_i\rvert=1$.

## 4. Mathematics

### 4.1 Sort key

For each currency, using timestamps strictly before the fill,

$$
D_i(t,T) = \ln S_i(t) - \ln F_i(t,T) \approx r_{f,i}-r_d
$$

Same $D$ as carry, now used as a cross-sectional score rather than a single-pair sign. Default $T=$ 1 month. Sort $i=1,\ldots,N$ on $D_i$. With few currencies, quantiles are halves or thirds, not deciles. Default: thirds.

If $N=9$ G10 ex-USD, thirds are three names per tail. One pegged name in $Q_H$ is one-third of the long leg. Exclude pegs in the universe step, not after the sort has already used them.

### 4.2 Leg weights

Long $Q_H$, short $Q_L$. Equal weights within each leg, or inverse-vol $1/\sigma_i$. Let $n_H=\lvert Q_H\rvert$ and $n_L=\lvert Q_L\rvert$. Uniform dollar-neutral:

$$
w_i = \frac{1}{2n_H}\quad i\in Q_H,\qquad w_i = -\frac{1}{2n_L}\quad i\in Q_L,\qquad w_i=0\text{ else}
$$

Each tail carries gross $1/2$, so net is zero when both tails are non-empty. Middle quantile is flat: those names are not “weak longs.” Inverse-vol: replace $1/n$ by $1/\sigma_i$ inside each leg, then scale each leg so it carries gross $1/2$. $\sigma_i$ ends before the fill. If $n_L=0$, this formula is undefined; the implementation must rebuild or refuse, not silently set the long leg to gross 1.

The two constraints

$$
\sum_i w_i = 0
$$

Net zero is what makes the book HML rather than dollar carry. After any drop, both this and the next identity must be rebuilt. Keeping $Q_H$ and deleting $Q_L$ without rebuild fails this test on purpose.

$$
\sum_i \lvert w_i\rvert = 1
$$

Gross-one is the budget. Both identities must hold after every rebuild. Tests check them to `1e-8`.

### 4.3 Holding-period P&L

Long foreign notional $N_{\mathrm{fx},i}$ settles in domestic on $S_i(t+T)-F_i(t,T)$:

$$
\mathrm{P\&L} = \sum_i N_{\mathrm{fx},i}\bigl(S_i(t+T)-F_i(t,T)\bigr) - \mathrm{costs}
$$

Same forward settlement as `006`, now with mixed signs. Costs include both legs’ spreads. EM points on $Q_H$ and G10 points on $Q_L$ are not the same number; using a single mid-spread understates the long-EM / short-G10 book. Report return on gross $I$, Sharpe on non-overlapping months, and

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

Quantile migration (a name entering or leaving $Q_H$) is the turnover driver. Track CIP basis as a **separate** residual. It is not HML-FX P&L. If you do $X$ = add CIP residual to this sum, you have booked a funding-stress price as carry alpha.

## 5. Step-by-step algorithm

1. **Universe.** G10 and liquid EM vs USD (or vs a chosen numeraire). Exclude pegs and non-deliverable names unless NDF liquidity is explicit. This step exists because a pegged high policy rate is convertibility risk, not a carry signal, and it poisons a three-name tail.
2. **Discount.** Compute $D_i$ from spot and 1m forwards dated $\le t_2<t_{\mathrm{fill}}$. This step exists to keep $D$ causal. Same-fixing $D$ and fill is delay-0.
3. **Quantiles.** Sort on $D_i$. Default three buckets. Require $n_H,n_L\ge 1$. This step exists so HML is two-sided. If either tail is empty, stop; do not emit a one-legged book.
4. **Weights.** Uniform or $1/\sigma_i$ inside legs; each leg gross $1/2$; net $0$. This step exists to enforce the two budget identities.
5. **Drop.** If a name has no borrow / no NDF, drop it and rebuild quantiles and $\gamma$ on the remainder. Do not keep $Q_H$ and skip $Q_L$. This step exists because a missing short leg is dollar carry in disguise.
6. **Size.** Map $w_i$ into forward notionals with gross $I$. Cap by traded spread / ADV analogue in FX. This step exists so a wide NDF cannot take a full $1/(2n_H)$ slot at an untradeable size.
7. **Blotter.** Forward intents only. Never live routing. This step exists because the spec is research.
8. **Rebalance.** Monthly on the fixing calendar. This step exists so last month’s $D$ is not reused without a new fixing.

## 6. Execution protocol

- Default fill: next fixing after $D$ is known. Delay-0 same-fixing is research-only. If you do $X$ = trade the WM print that produced $D$, the backtest lies.
- Exclude pegs. A peg with a high policy rate is not a carry signal; it is convertibility risk.
- If all quotes are vs USD, a one-legged implementation (long $Q_H$ only) is a dollar bet. This spec requires both legs.

## 7. Data contract

Required, point-in-time:

- Spot mid and bid/ask
- Outright 1m forwards or forward points
- Tenor rates for the CIP diagnostic
- Fixing calendar and holiday gaps
- NDF vs deliverable flag
- Vol for inverse-vol weights (60d default)

Not used by this spec: equity fundamentals, futures COT.

No look-ahead on fixing timestamps. A revised WM print after $t$ does not change $D_t$. If you do $X$ = rebuild historical $D$ after a WM restatement, ranks at $t$ were not the live ranks. If you do $X$ = leave a missing $Q_L$ name at last month’s weight while others re-sort, neutrality is broken. Quote convention must be uniform; mixing USD-per-foreign with foreign-per-USD inside the sort flips a name’s $D$ sign.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor $T$ | 1 month | |
| quantile | $1/3$ | halves if $N$ is tiny |
| weights | equal | or $1/\sigma_i$ |
| universe | G10 ex-USD | liquid EM optional |
| delay | 1 fixing | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.fx_high_minus_low_carry` with:

1. `discount(spot, forward) -> pd.Series` — $D_i$, no look-ahead.
2. `quantiles(D, q=1/3) -> tuple[pd.Index, pd.Index]` — $Q_H,Q_L$.
3. `weights(D, sigma=None, q=1/3) -> pd.Series` — $\sum w_i=0$ and $\sum\lvert w_i\rvert=1$ to `1e-8`.
4. `blotter(weights, forwards, I) -> list[OrderIntent]` — never live routing.
5. `pnl(notionals, spot_T, forward_entry, costs) -> float` — matches the forward P&L identity.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Crash in $Q_H$.** High-yield currencies gap together; the short $Q_L$ (often JPY, CHF) does not offset a full EM unwind.
- **Dollar factor.** If the short leg is missing, HML collapses to dollar carry (`053`).
- **CIP / NDF.** Traded discounts are not CIRP discounts under funding stress.
- **Small $N$.** Thirds of G10 are three names per leg; one pegged name poisons the sort.

## 11. Acceptance tests

- Three currencies, $D=(2,0,-2)$, equal $\sigma$, $q=1/3$ → $w=(+1/2,0,-1/2)$, $\sum w=0$, $\sum\lvert w\rvert=1$.
- Adding a constant $c$ to every $D_i$ must not change ranks or weights (dollar rate cancels).
- Permuting spots after the decision timestamp must not change $w_t$.
- Dropping the entire $Q_L$ without rebuild must **fail** the neutrality test; the implementation must rebuild or refuse.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
