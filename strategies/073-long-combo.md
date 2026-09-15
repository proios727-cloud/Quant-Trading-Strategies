---
rank: 73
slug: long-combo
title: "Long Combo"
asset_class: "options"
style: "bullish capital-gain / risk reversal"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 073. Long Combo

| Field | Value |
|---|---|
| Popularity rank (this kit) | 73 of 101 |
| Why it sits here | OTM risk reversal: long OTM call, short OTM put. Standard FX and equity skew trade; also a directional overlay. |
| Aliases | long risk reversal |
| Asset class | options |
| Style | bullish capital-gain / risk reversal |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long an OTM call $K_1$ and short an OTM put $K_2 < K_1$, same expiry. Bullish. Same payoff family as a synthetic long forward, but with OTM strikes so there is a dead zone between $K_2$ and $K_1$. Typically 25-delta each wing.

You are betting that spot finishes above the relevant break-even, with unlimited upside through the call. You are selling put skew: in equities, OTM puts are usually richer than OTM calls, so you are often paid ($H<0$) to be long the reversal. That is still a short-put crash. You are not vol-neutral unless you delta-hedge; unhedged, this is a directional crash-short. Same listed legs as `086`; here the thesis can be directional.

The typical user wants a cheap bullish overlay or a skew credit with a view. Horizon is one expiry, often 1–3 months at 25-delta or 16-delta. Size off $L_{\max}=K_2+H$, not off the credit. Do not warehouse the short put without the long call.

## 2. First principles

Two listed options, same expiry, quantity $1:1$. The long OTM call pays $(S_T-K_1)_+$. The short OTM put pays $-(K_2-S_T)_+$. Subtract net premium paid $H$:

$$
f_T = (S_T - K_1)_+ - (K_2 - S_T)_+ - H
$$

Unlike `045`/`065`, the strikes differ, so the kinks do not cancel to a pure forward. Between the strikes both options can be out of the money. $H$ is the skew harvest (often a credit) and a parallel shift. Quantity other than $1:1$ is a ratio, not a combo.

Strike order is

$$
K_1 > K_2
$$

Call above, put below. If you reverse the strikes you have built a different (usually nonsense) package or a short combo with the rights swapped. `validate` must enforce this. Typical 25-delta wings sit on either side of $S_0$.

Region by region:

- $S_T \ge K_1$: call in the money, put worthless, so $f_T = S_T - K_1 - H$. Upside is unlimited.
- $K_2 < S_T < K_1$: both out of the money, so $f_T = -H$. A credit ($H<0$) pays in the dead zone; a debit ($H>0$) loses $H$ there.
- $S_T \le K_2$: put in the money, call worthless, so $f_T = -(K_2 - S_T) - H = S_T - K_2 - H$. At $S_T = 0$ this is $-K_2 - H$.

This **sells** put skew. In equities, OTM puts are usually richer than OTM calls, so you are often paid ($H<0$) to be long the reversal. That is a skew harvest with directional crash risk, not a vol-neutral trade unless you delta-hedge.

**Payoff sketch.** 25-delta call $K_1$, 25-delta put $K_2$, small credit. At $S_T=0$, $f_T=-(K_2+H)=-L_{\max}$ (crash, short put). In the dead zone, $f_T=-H$ (keep the credit). Far above $K_1$, $f_T=S_T-K_1-H$ rises without bound. The sketch is a long forward with a flat shelf between the wings.

That is the whole strategy. Same legs as `086`; here the thesis can be directional.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_2 < K_1$ | short OTM put strike, long OTM call strike |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast$ | expiry break-even where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

One long call, one short put. Same expiry. Quantity ratio $1:1$.

## 4. Mathematics

### 4.1 Premium

$H$ can be a credit or a debit depending on skew. Equity 25-delta reversals are often credits because puts are rich. Record $H$ from call ask minus put bid (plus fees). A mid-to-mid credit that never fills is not skew harvest. If the smile does not show put-over-call richness and you still want the trade, you are in the directional `073` thesis, not a “free” skew coupon.

### 4.2 Terminal payoff

$$
f_T = (S_T - K_1)_+ - (K_2 - S_T)_+ - H
$$

Implement this exactly. The dead zone is load-bearing: both positive parts vanish and P&L is $-H$. Tests that only check $S_T=0$ and $S_T\to\infty$ will miss a wrong $H$ sign in the middle.

### 4.3 Break-evens

If you pay a debit, the break-even sits above the call strike:

$$
S^\ast = K_1 + H \qquad (H>0)
$$

Spot must climb through the call and then earn back $H$. The dead zone is a loss of $D$. Pick this branch only when $H>0$.

If you receive a credit, the break-even sits above the put strike (inside or below the dead zone, depending on size):

$$
S^\ast = K_2 + H \qquad (H<0)
$$

Because $H$ is negative, $K_2+H<K_2$. Below that print the short put has given the credit back. Above it — including the whole dead zone — you are non-negative at expiry. This is why a skew credit “pays if nothing happens.”

If the package is zero-premium, any finish in the dead zone is a break-even:

$$
K_2 \le S^\ast \le K_1 \qquad (H=0)
$$

The whole shelf is $f_T=0$. Metrics should report a band, not a single print. Mixing the three branches is a common agent bug.

### 4.4 Max profit and loss

$$
P_{\max} = \text{unlimited}
$$

At $S_T = 0$:

$$
L_{\max} = K_2 + H
$$

Unlimited on the call, capped crash on the put at roughly the put strike plus net premium. Size off $L_{\max}$. A credit ($H<0$) slightly reduces the crash loss; it does not remove it. Stock at zero is the stress, not a 5% dip that stays above $K_2$.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. If you delta-hedge, expiry identities no longer describe P&L; P&L becomes roughly the change in the risk-reversal mark. Carry $\Delta, \Gamma, \Theta, \nu$. Unhedged, this is a crash-short directional book. Calling the unhedged mark “skew P&L” is how a spot-down month gets mis-attributed.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed OTM call and OTM put, same expiry. 25-delta (or 16-delta) wings on a posted smile. Without a smile you cannot identify the wings this file names.
2. **Strikes.** $K_1 > S_0 > K_2$, typically 25-delta each. Same $T$. Delta from a surface dated $\le t_{\mathrm{fill}}$; a future-dated smile is look-ahead.
3. **Legs.** Buy 1 call $K_1$, sell 1 put $K_2$. Quantity ratio $1:1$. Same legs as `086`; the hedge flag is what differs.
4. **Premium.** Compute $H$. Record whether the package is a skew credit. Fill at the call ask and put bid.
5. **Metrics.** Store the appropriate $S^\ast$ branch, $P_{\max}$ unlimited, $L_{\max}=K_2+H$. The branch depends on the sign of $H$; do not hard-code $K_1+H$.
6. **Blotter.** Emit a two-leg risk-reversal intent. Do not route live orders.
7. **Hold.** Hold to expiry or manage as a directional overlay. A gap through $K_2$ is the designed left tail. Unhedged, do not relabel this as `086`.

## 6. Execution protocol

- Typical wings: 25-delta or 16-delta, tenor 1–3 months. Mixing tenors is a diagonal, not this combo.
- This sells put skew. In equities you are often paid to be long the reversal. That is still a short-put crash.
- Do not treat the unhedged combo as market-neutral vol. Delta-hedge only if the thesis is the skew mark, as in `086`.
- Size off $L_{\max}=K_2+H$, not off the credit. Sizing off credit is how a “paid to own the reversal” book is geared into a crash.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **OTM call and OTM put**
- Delta (or a smile) so 25-delta / 16-delta wings can be identified
- Dividends and rates if deltas are model-based
- At expiry: settlement print and American early-exercise events on the short put

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them. Delay-0 mids for $H$ are research-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| wings | 25-delta or 16-delta | $K_1$ call, $K_2$ put |
| quantity ratio | $1:1$ | one long call, one short put |
| tenor | 1–3 months | same expiry |
| $H$ | market | often a credit in equity skew |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_combo` with:

1. `legs(spec) -> list[Leg]` — long call $K_1$, short put $K_2$, $K_1 > K_2$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*` under the correct $H$ branch, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1 > K_2$, qty $1:1$; $L_{\max}=K_2+H$ at $S_T=0$; $f_T(S^\ast)=0$ on the matching branch.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Crash.** You are short the put. $L_{\max}=K_2+H$. A gap through the put wing on an index shock is the path; the dead-zone credit does not offset it.
- **Unlimited upside** only on the call side; that is the thesis, not a hedge. Do not describe this as defined-risk.
- **Not vol-neutral** unless delta-hedged. Spot down moves the reversal against you. A backtest that reports “skew P&L” on an unhedged book is lying about the source.
- **Assignment** on the short American put. You can be long stock you did not want, versus a still-open OTM call.
- **Wrong break-even branch.** Using $K_1+H$ on a credit structure invents a hurdle that is not there.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $(S_T-K_1)_+ - (K_2-S_T)_+ - H$.
- At $S_T=0$, $f_T = -(K_2+H) = -L_{\max}$.
- Break-even branch: $H>0 \Rightarrow S^\ast=K_1+H$; $H<0 \Rightarrow S^\ast=K_2+H$; $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- Reject $K_1 \le K_2$ or quantity ratio other than $1:1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves $S^\ast$ only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
