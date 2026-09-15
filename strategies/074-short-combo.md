---
rank: 74
slug: short-combo
title: "Short Combo"
asset_class: "options"
style: "bearish capital-gain / short risk reversal"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 074. Short Combo

| Field | Value |
|---|---|
| Popularity rank (this kit) | 74 of 101 |
| Why it sits here | Mirror of the long combo. Standard listed and OTC risk reversal, used when the trader is bearish and willing to sell OTM call skew. |
| Aliases | short risk reversal |
| Asset class | options |
| Style | bearish capital-gain / short risk reversal |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long an OTM put $K_1$ and short an OTM call $K_2 > K_1$, same expiry. Bearish capital-gain. Same payoff family as a short synthetic forward, but with OTM strikes so there is a dead zone between $K_1$ and $K_2$. Typically 25-delta each wing. Unbounded loss sits on the short call, not the long put.

You are betting that spot finishes below the relevant break-even, with defined profit if it goes to zero. You are selling the call wing to pay for crash convexity. Equity call skew is usually cheaper than put skew, so this package is often a debit versus `073`. You are not running a defined-risk bear put spread: the short call is uncovered. Size off the rally tail, not off collected credit (or the small debit).

The typical user is bearish and willing to sell OTM call skew. Horizon is one expiry at 25-delta or 16-delta. Do not warehouse the short call without the long put. Flatten on a gap through $K_2$. The long put does not cap the call.

## 2. First principles

Two listed options, same expiry, quantity $1:1$. The long OTM put pays $(K_1-S_T)_+$. The short OTM call pays $-(S_T-K_2)_+$. Subtract net premium paid $H$:

$$
f_T = (K_1 - S_T)_+ - (S_T - K_2)_+ - H
$$

This is the mirror of `073`. Different strikes leave a dead zone. $H$ is often a debit in equity because the call you sell is cheaper than the put you buy. Quantity $1:1$ keeps it a reversal, not a ratio.

Strike order is

$$
K_2 > K_1
$$

Call above, put below. Reverse that and you have the long combo’s strikes with the rights swapped — still a combo, but not this file’s metrics. Enforce $K_2>K_1$ in `validate`.

Region by region:

- $S_T \le K_1$: put in the money, call worthless, so $f_T = K_1 - S_T - H$. At $S_T = 0$ this is $K_1 - H$.
- $K_1 < S_T < K_2$: both out of the money, so $f_T = -H$.
- $S_T \ge K_2$: call in the money, put worthless, so $f_T = -(S_T - K_2) - H = K_2 - S_T - H$. Loss is unlimited as $S_T$ rallies.

Equity call skew is usually cheaper than put skew, so this package is often a debit versus the long combo. You are selling the call wing to pay for crash convexity.

**Payoff sketch.** 25-delta put $K_1$, 25-delta call $K_2$. At $S_T=0$, $f_T=K_1-H=P_{\max}$ (crash, long put). In the dead zone, $f_T=-H$ (lose a debit, keep a credit). Far above $K_2$, $f_T=K_2-S_T-H\to-\infty$. The sketch is a short forward with a flat shelf between the wings; the missing wall is the rally.

That is the whole strategy. Defined profit, undefined loss. Size off the rally tail.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2$ | long OTM put strike, short OTM call strike |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast$ | expiry break-even where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

One long put, one short call. Same expiry. Quantity ratio $1:1$.

## 4. Mathematics

### 4.1 Premium

Net credit or small debit depending on skew. Equity 25-delta short reversals are often debits because the call you sell is cheaper than the put you buy. That debit is the price of crash convexity, not a reason to skip $L_{\max}$ unlimited. Fill at the put ask and call bid.

### 4.2 Terminal payoff

$$
f_T = (K_1 - S_T)_+ - (S_T - K_2)_+ - H
$$

Implement this exactly. Dead-zone P&L is $-H$. Tests must cover $0$, the shelf, and a large $S_T$. A sign error on the call turns this into a long combo.

### 4.3 Break-evens

If you pay a debit, the break-even sits below the put strike:

$$
S^\ast = K_1 - H \qquad (H>0)
$$

Spot must fall through the put and then earn back $H$. The dead zone is a loss of $D$. Use this branch only when $H>0$.

If you receive a credit, the break-even is

$$
S^\ast = K_2 - H \qquad (H<0)
$$

$H$ is negative, so $K_2-H$ sits *above* the call strike by the credit amount. The dead zone still keeps the credit; the short call gives that credit back only once spot is through $K_2$ and then through $S^\ast$. Above $S^\ast$ you have lost the credit and more. Metrics must use this branch only when $H<0$.

If the package is zero-premium, any finish in the dead zone is a break-even:

$$
K_1 \le S^\ast \le K_2 \qquad (H=0)
$$

The shelf is flat at zero. Report a band. Mixing branches with `073` (opposite $H$ formulas) is a common bug.

### 4.4 Max profit and loss

At $S_T = 0$:

$$
P_{\max} = K_1 - H
$$

$$
L_{\max} = \text{unlimited}
$$

Unbounded loss sits on the short call, not the long put. $P_{\max}$ is the crash prize, finite. Do not report unlimited profit. Size, stops, and ADV live on the call tail.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. Delta-hedging replaces expiry P&L with a short-reversal / long-put-skew book. Carry $\Delta, \Gamma, \Theta, \nu$. Gap-up through $K_2$ is the unhedged disaster path. A hedged book still has jump risk on the short call; expiry $P_{\max}$ will not describe that week.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed OTM put and OTM call, same expiry. 25-delta (or 16-delta) wings. Same smile discipline as `073`.
2. **Strikes.** $K_2 > S_0 > K_1$, typically 25-delta each. Same $T$. Deltas dated $\le t_{\mathrm{fill}}$.
3. **Legs.** Buy 1 put $K_1$, sell 1 call $K_2$. Quantity ratio $1:1$. Mirror of the long combo; do not mix a long call into this ticket.
4. **Premium.** Compute $H$. Document that $L_{\max}$ is unlimited regardless of credit. A credit does not make this defined-risk.
5. **Metrics.** Store the appropriate $S^\ast$ branch, $P_{\max}=K_1-H$, $L_{\max}$ unlimited. Branch on $\mathrm{sign}(H)$.
6. **Blotter.** Emit a two-leg short risk-reversal intent. Do not route live orders.
7. **Hold.** Hold to expiry or manage as a directional overlay. Flatten on a gap through $K_2$. The put will not save the call.

## 6. Execution protocol

- Typical wings: 25-delta or 16-delta, tenor 1–3 months.
- Gap-up through $K_2$ is the unbounded loss path; size off that tail, not off collected credit.
- Equity call skew is usually cheaper than put skew, so this is often a debit versus `073`. Paying the debit does not cap the rally.
- Do not warehouse the short call without the long put. Legging the call first is a naked short call.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **OTM put and OTM call**
- Delta (or a smile) so 25-delta / 16-delta wings can be identified
- Dividends and rates if deltas are model-based
- At expiry: settlement print and American early-exercise events on the short call

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| wings | 25-delta or 16-delta | $K_1$ put, $K_2$ call |
| quantity ratio | $1:1$ | one long put, one short call |
| tenor | 1–3 months | same expiry |
| $H$ | market | often a debit vs the long combo |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_combo` with:

1. `legs(spec) -> list[Leg]` — long put $K_1$, short call $K_2$, $K_2 > K_1$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*` under the correct $H$ branch, `P_max`, `L_max`, debit/credit flag. Document unlimited loss on the short call.
5. `validate(spec)` — $K_2 > K_1$, qty $1:1$; $P_{\max}=K_1-H$ at $S_T=0$; $f_T(S^\ast)=0$ on the matching branch.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Rally.** Short call is uncovered. Defined profit, undefined loss. A squeeze or buyout through $K_2$ is the path.
- **Skew debit.** Equity call wings are usually cheaper than put wings, so you often pay to be short the reversal. The debit is not a reason to treat $L_{\max}$ as $H$.
- **Assignment** on the short American call (dividends). You can be short stock versus a still-open OTM put.
- **False hedge.** The long put does not cap the call. Describing this as a “collar without stock” hides the uncovered call.
- **Wrong break-even branch.** Copying `073`’s $K_1+H$ / $K_2+H$ rules with the wrong signs will fail tests and mis-state the shelf.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $(K_1-S_T)_+ - (S_T-K_2)_+ - H$.
- At $S_T=0$, $f_T = K_1 - H = P_{\max}$.
- Break-even branch: $H>0 \Rightarrow S^\ast=K_1-H$; $H<0 \Rightarrow S^\ast=K_2-H$; $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- Reject $K_2 \le K_1$ or quantity ratio other than $1:1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves $S^\ast$ only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
