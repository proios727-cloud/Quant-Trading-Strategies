---
rank: 77
slug: short-iron-condor
title: "Short Iron Condor"
asset_class: "options"
style: "long volatility / debit / defined risk"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 077. Short Iron Condor

| Field | Value |
|---|---|
| Popularity rank (this kit) | 77 of 101 |
| Why it sits here | Defined-risk long-vol alternative to a long strangle. Four-legged debit. |
| Aliases | — |
| Asset class | options |
| Style | long volatility / debit / defined risk |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short an OTM put $K_1$, long an OTM put $K_2$, long an OTM call $K_3$, short an OTM call $K_4$, with equidistant spacing $\kappa$. Net debit. Neutral capital-gain (long vol). Long the inner strangle, short the outer strangle. This file’s “short” iron condor is the **debit** structure.

You are betting on a move through the inner strikes, large enough to recoup $D$, capped at the outer wings. You are not running a naked long strangle; $P_{\max}=\kappa-D$. You are not running a credit iron condor (short the inner, long the outer): that structure wants a quiet tape and is the opposite of this file. Broker names often invert long/short; match the legs.

The typical user wants long vol cheaper than a strangle, accepting the cap. Horizon is one expiry. Reject $D\ge\kappa$ with $\kappa$ the wing width $K_2-K_1=K_4-K_3$. Theta is negative while spot sits between $K_2$ and $K_3$. Enter as four legs with a net-debit limit. Do not warehouse the inner strangle without the wings.

## 2. First principles

Four listed options, same expiry, one-lot each. The inner strangle pays $(K_2-S_T)_+ + (S_T-K_3)_+$. The outer short put pays $-(K_1-S_T)_+$. The outer short call pays $-(S_T-K_4)_+$. Subtract the debit $D$:

$$
f_T = (K_2 - S_T)_+ + (S_T - K_3)_+ - (K_1 - S_T)_+ - (S_T - K_4)_+ - D
$$

Inner longs are the long-vol engine; outers cap each side. $D$ is the budget for the move. Compared with `076`, the body is a *strangle* (gap between $K_2$ and $K_3$), not a straddle, so the dead zone is wider and you need a larger move to get paid. One-lot each keeps the caps equal to the wing width.

Equidistant strikes mean

$$
K_4 - K_3 = K_3 - K_2 = K_2 - K_1 = \kappa
$$

The default is equal consecutive gaps. $P_{\max}$ uses the *wing* width $K_2-K_1=K_4-K_3$. If the inner gap $K_3-K_2$ is wider than the wings, the dead zone is wider but the cap is still the wing width. `validate` should still require equal wings even if the caller widens the belly.

Between $K_2$ and $K_3$ every option expires out of the money and $f_T = -D$. That is the quiet-tape loss: you paid for a move that stayed inside the inner strangle.

Far below $K_1$, the two puts become a spread worth $\kappa$, so $f_T = \kappa - D$. Far above $K_4$, the two calls become a spread worth $\kappa$, so again $f_T = \kappa - D$. The outer wings cap the long strangle.

Break-evens sit just outside the inner strikes: you need a sizable move, but not an unlimited one. That is the whole strategy. Cheaper than a long strangle only if you are willing to cap the payoff.

**Payoff sketch.** Inner strangle $K_2,K_3$, outer wings $K_1,K_4$, debit $D$. At $S_T=0$ (through the put wing), $f_T=\kappa-D=P_{\max}$. Between $K_2$ and $K_3$, $f_T=-D$ (dead zone). Far above $K_4$, $f_T=\kappa-D$ again. The sketch is a wide flat hole with chopped-off arms, not a V like the iron butterfly.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2 < K_3 < K_4$ | short put, long put, long call, short call |
| $\kappa$ | spacing, $K_2-K_1=K_3-K_2=K_4-K_3$ in the equidistant default |
| $(x)_+$ | $\max(x,0)$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Long the inner strangle, short the outer strangle. Same expiry. Require $D < \kappa$ with $\kappa$ the wing width $K_2-K_1 = K_4-K_3$.

## 4. Mathematics

### 4.1 Premium

Net debit $D > 0$: the inner strangle costs more than the outer strangle brings in. Reject if $D \ge \kappa$. A debit that large cannot profit at the wings. Fill inner asks and outer bids; mids understate $D$ and make break-evens look closer than they are.

### 4.2 Terminal payoff

$$
f_T = (K_2 - S_T)_+ + (S_T - K_3)_+ - (K_1 - S_T)_+ - (S_T - K_4)_+ - D
$$

Four intrinsics. Tests must show $-D$ on the whole interval $[K_2,K_3]$, not only at a single ATM point. That interval is what distinguishes the condor from `076`.

### 4.3 Break-evens

Lower break-even, in the put wing $(K_1, K_2)$:

$$
S^\ast_{\mathrm{down}} = K_2 - D
$$

The long inner put must earn $D$. If $D$ exceeds the wing width, this print would sit at or below $K_1$ and the structure cannot cross into profit — another reading of $D<\kappa$.

Upper break-even, in the call wing $(K_3, K_4)$:

$$
S^\ast_{\mathrm{up}} = K_3 + D
$$

Symmetric. The inner gap $K_3-K_2$ does not appear in these two formulas: you start counting $D$ from the inner strikes outward. A wider belly means more of the tape is a dead-zone loss before you even reach these prints.

### 4.4 Max profit and loss

Outside the outer wings:

$$
P_{\max} = \kappa - D
$$

Inside the inner strangle:

$$
L_{\max} = D
$$

Here $\kappa$ is the wing width. If only the wings are equal and the inner gap $K_3-K_2$ is wider, $P_{\max}$ is still that wing width minus $D$, and the dead zone between $K_2$ and $K_3$ is wider. Do not substitute the inner gap for $\kappa$ in $P_{\max}$. A crash pays the put-wing width, not the distance from spot to $K_4$.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $D$. Theta is negative. Carry $\Delta, \Gamma, \Theta, \nu$ if you hedge. The expiry identities assume European-style settlement. A quiet tape inside the belly realizes $L_{\max}$ slowly via theta; a late move that stops between $K_2$ and $K_3$ still loses $D$.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed options at four strikes, put rights on $K_1,K_2$ and call rights on $K_3,K_4$. Four two-sided markets; skip if an outer wing is a one-sided quote (the cap would be fictional).
2. **Strikes.** Same grid as the credit iron condor, inverted: $K_1 < K_2 < K_3 < K_4$. Default equidistant $\kappa$. Inverting a credit condor’s strikes without inverting the sides is a common construction error.
3. **Legs.** Sell 1 put $K_1$, buy 1 put $K_2$, buy 1 call $K_3$, sell 1 call $K_4$. One-lot each. Inner long, outer short: debit long-vol.
4. **Premium.** Compute $D$. Reject if $D \ge \kappa$ with $\kappa = K_2-K_1 = K_4-K_3$. The reject uses wing width, not the belly.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}=K_2-D$, $S^\ast_{\mathrm{up}}=K_3+D$, $P_{\max}=\kappa-D$, $L_{\max}=D$.
6. **Blotter.** Enter as one iron-condor ticket. Do not route live orders. Net-debit limit on four legs.
7. **Hold.** You need a move through the inner strikes. Flatten if you no longer want to pay theta. Sitting in the belly into expiry is how $L_{\max}$ is realized.

## 6. Execution protocol

- Use when you want long vol with a capped gain $\kappa-D$ and no unlimited tail.
- Cheaper than a long strangle only if you are willing to cap the payoff. A backtest that compares this to a strangle without noting the cap will look like underperformance on crash days by design.
- Match the payoff, not the broker name: some screens call this a long iron condor. This file’s “short” is the debit structure.
- Enter as four legs with a net-debit limit. Do not warehouse the inner strangle without the wings.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **four strikes, two puts and two calls**
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the short outer wings

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them. Delay-0 mids for $D$ are research-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| strike grid | same as the credit iron condor, inverted | $K_1<K_2<K_3<K_4$ |
| $\kappa$ | equidistant consecutive gaps | wing width is what enters $P_{\max}$ |
| quantity | one-lot each | four legs |
| tenor | 1 week to 3 months | same expiry |
| $D$ | market | must satisfy $D < \kappa$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_iron_condor` with:

1. `legs(spec) -> list[Leg]` — short put $K_1$, long put $K_2$, long call $K_3$, short call $K_4$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down`, `S*_up`, `P_max`, `L_max`, debit flag.
5. `validate(spec)` — $K_1<K_2<K_3<K_4$, equal wings, $P_{\max}=\kappa-D$, $L_{\max}=D$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined debit.** Needs a sizable move. Theta is negative. Loss $D$ if spot stays between $K_2$ and $K_3$. A range-bound month is the usual failure, not a crash (a crash pays $P_{\max}$).
- **Capped gain.** $P_{\max}=\kappa-D$; a crash or melt-up does not pay like a naked strangle. The outer shorts are the reason.
- **Wing assignment** on the short outers. The cap assumes those shorts settle to intrinsic.
- **Naming clash.** Broker “long/short iron condor” may invert this payoff. Match the legs. Implementing a credit condor under this module name is a quiet-tape sale, not this spec.
- **Wrong $\kappa$.** Using the inner gap $K_3-K_2$ in $P_{\max}$ overstates the crash prize.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals the listed-leg intrinsics minus $D$.
- For $K_2 \le S_T \le K_3$, $f_T=-D=-L_{\max}$. At $S_T \le K_1$ and $S_T \ge K_4$, $f_T=\kappa-D=P_{\max}$.
- $f_T(S^\ast_{\mathrm{down}})=f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject $K_1 \ge K_2$ or mismatched wing widths.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
