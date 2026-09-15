---
rank: 76
slug: short-iron-butterfly
title: "Short Iron Butterfly"
asset_class: "options"
style: "long volatility / debit"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 076. Short Iron Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 76 of 101 |
| Why it sits here | Debit iron butterfly: long ATM straddle, short OTM wings. Defined-risk long straddle. |
| Aliases | — |
| Asset class | options |
| Style | long volatility / debit |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short an OTM put $K_1$, long an ATM put and an ATM call $K_2$, short an OTM call $K_3$, with equal wings $\kappa = K_2 - K_1 = K_3 - K_2$. Net debit. Neutral capital-gain: a defined-risk long straddle. This file’s “short” iron butterfly is the **debit / long-vol** structure (long the body, short the wings).

You are betting that $\lvert S_T-K_2\rvert > D$: a move large enough to recoup the debit, capped at the wings. You are not running a naked long straddle; $P_{\max}=\kappa-D$. You are not running a credit iron butterfly (short the body): that structure wants the pin and is the opposite of this file. Broker screens often invert the long/short name; match the legs.

The typical user wants long vol with a budget $D$. Horizon is one expiry. Reject $D\ge\kappa$. Theta is negative until a move arrives. Size off ATM straddle ADV, not off $D$ alone. Enter as four legs with a net-debit limit; do not warehouse the long straddle unhedged by the wings.

## 2. First principles

Four listed options, same expiry, one-lot each. Long ATM straddle plus short OTM strangle. The straddle pays $(K_2-S_T)_+ + (S_T-K_2)_+$. The short put wing pays $-(K_1-S_T)_+$. The short call wing pays $-(S_T-K_3)_+$. Subtract the debit $D$:

$$
f_T = (K_2 - S_T)_+ + (S_T - K_2)_+ - (K_1 - S_T)_+ - (S_T - K_3)_+ - D
$$

The straddle is the long-vol engine; the wings cap it. $D$ is what you paid for the move. Missing a wing turns this into a short vertical on one side plus a naked option on the other. One-lot each is required so the caps equal $\kappa$.

Equal spacing means

$$
\kappa = K_2 - K_1 = K_3 - K_2
$$

Equal wings make $P_{\max}=\kappa-D$ the same on both tails. A broken wing still caps, but this file’s closed forms assume equal $\kappa$. $\kappa$ is the width of each vertical that remains once the straddle is deep in the money.

At $S_T = K_2$ every option is at or out of the money and $f_T = -D$. That is the pin loss: you paid for a move that did not arrive.

Far below $K_1$, the long ATM put and short OTM put become a put spread worth $\kappa$, so $f_T = \kappa - D$. Far above $K_3$, the long ATM call and short OTM call become a call spread worth $\kappa$, so again $f_T = \kappa - D$. The wings cap the long straddle.

You need $\lvert S_T - K_2\rvert > D$ to get through the break-evens. Theta is negative. That is the whole strategy: long vol with a budget $D$ and a known $P_{\max}$.

**Payoff sketch.** ATM straddle, equal OTM wings, debit $D<\kappa$. At $S_T=0$ (through the put wing), $f_T=\kappa-D=P_{\max}$. At $S_T=K_2$, $f_T=-D=-L_{\max}$ (pin). Far above $K_3$, $f_T=\kappa-D$ again. The sketch is a V with the bottoms of the arms chopped off at $\kappa-D$.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2 < K_3$ | short OTM put, long ATM straddle, short OTM call |
| $\kappa$ | wing spacing, $\kappa = K_2-K_1 = K_3-K_2$ |
| $(x)_+$ | $\max(x,0)$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Long ATM straddle, short OTM strangle. Same expiry. Require $D < \kappa$.

## 4. Mathematics

### 4.1 Premium

Net debit $D > 0$: the ATM straddle costs more than the OTM strangle brings in. Reject if $D \ge \kappa$. A debit that large cannot profit even at the wings. Compute $D$ from straddle asks minus wing bids; mids make the structure look cheaper than it fills.

### 4.2 Terminal payoff

$$
f_T = (K_2 - S_T)_+ + (S_T - K_2)_+ - (K_1 - S_T)_+ - (S_T - K_3)_+ - D
$$

Implement all four intrinsics. Tests at $K_2$ and outside the wings are the two extrema. Dropping the short call wing leaves unlimited upside *and* a different $P_{\max}$.

### 4.3 Break-evens

Lower break-even, below $K_2$:

$$
S^\ast_{\mathrm{down}} = K_2 - D
$$

The long put must earn back $D$. Between $S^\ast_{\mathrm{down}}$ and $K_2$ you are still underwater. Fees that inflate $D$ push this print further from $K_2$ (harder hurdle).

Upper break-even, above $K_2$:

$$
S^\ast_{\mathrm{up}} = K_2 + D
$$

Symmetric on the call. You need a move of more than $D$ in either direction. Unlike a naked straddle, getting far beyond the wings does not increase profit past $\kappa-D$.

### 4.4 Max profit and loss

Outside the wings:

$$
P_{\max} = \kappa - D
$$

At the pin $S_T = K_2$:

$$
L_{\max} = D
$$

Defined-risk long vol. A crash or melt-up pays the wing width net of debit, not the naked-straddle payoff. Quiet tape loses $D$. Both numbers should appear in metrics; a tool that only stores $D$ hides the cap.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $D$. $P_{\max}$ / $L_{\max}$ are **expiry** quantities. Delta-hedging turns this into a long-gamma book with short vega on the wings. Carry $\Delta, \Gamma, \Theta, \nu$. Theta is negative until a move arrives. A hedged iron that never moves still pays theta on the straddle.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed options at three strikes, both rights at $K_2$, put at $K_1$, call at $K_3$. Four markets must exist; a missing ATM put is not “close enough.”
2. **Strikes.** ATM body $K_2 \approx S_0$, equal $\kappa$. Require $K_1 < K_2 < K_3$. Equal wings keep $P_{\max}$ symmetric.
3. **Legs.** Sell 1 put $K_1$, buy 1 put $K_2$, buy 1 call $K_2$, sell 1 call $K_3$. One-lot each. This is long straddle, short strangle — the debit iron.
4. **Premium.** Compute $D$. Reject if $D \ge \kappa$. The reject is the “cannot profit at the wings” gate.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}=K_2-D$, $S^\ast_{\mathrm{up}}=K_2+D$, $P_{\max}=\kappa-D$, $L_{\max}=D$.
6. **Blotter.** Enter as one iron-butterfly ticket. Do not route live orders. Four legs, net-debit limit.
7. **Hold.** You need $\lvert S_T-K_2\rvert > D$. Flatten if you no longer want to pay theta. Waiting through a quiet expiry is how $L_{\max}=D$ is realized.

## 6. Execution protocol

- Capped long-vol. Prefer this over a naked long straddle when you want a budget $D$ and a known $P_{\max}$.
- Match the payoff, not the broker name: some screens call this a long iron butterfly. This file’s “short” is the debit structure. Matching the wrong name inverts you into a pin sale.
- Enter as four legs with a net-debit limit. Do not warehouse the long straddle unhedged by the wings. A backtest that fills the straddle first and the wings later will show naked-straddle risk this spec does not allow.
- Cap size by ATM straddle ADV, not by $D$ alone.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **put $K_1$, put and call $K_2$, call $K_3$**
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the short wings

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K_2$ | ATM | long straddle |
| $\kappa$ | equal wings | $K_2-K_1=K_3-K_2$ |
| quantity | one-lot each | four legs |
| tenor | 1 week to 3 months | same expiry |
| $D$ | market | must satisfy $D < \kappa$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_iron_butterfly` with:

1. `legs(spec) -> list[Leg]` — short put $K_1$, long put $K_2$, long call $K_2$, short call $K_3$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive); debit $D$ is the negative of that credit.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down`, `S*_up`, `P_max`, `L_max`, debit flag.
5. `validate(spec)` — equal $\kappa$, $P_{\max}=\kappa-D$, $L_{\max}=D$ on a dense $S_T$ grid including $K_2$ and the wings.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **No move.** Needs $\lvert S_T-K_2\rvert > D$. Theta is negative. Loss $D$ at the pin. A quiet month is the usual failure, not a crash (a crash *pays* $P_{\max}$).
- **Capped gain.** $P_{\max}=\kappa-D$; a melt-up or crash does not pay like a naked straddle. Comparing this sleeve to a straddle without the cap will look like “left money on the table” by design.
- **Wing assignment** on the short OTM American options if the move is large. The cap assumes the shorts settle; assignment can gap the mark.
- **Naming clash.** Broker “long/short iron butterfly” may invert this payoff. Match the legs.
- **Look-ahead debit.** Delay-0 mids for $D$ make break-evens look closer than a delay-1 fill will deliver.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals the listed-leg intrinsics minus $D$.
- At $S_T=K_2$, $f_T=-D=-L_{\max}$. At $S_T \le K_1$ and $S_T \ge K_3$, $f_T=\kappa-D=P_{\max}$.
- $f_T(S^\ast_{\mathrm{down}})=f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject unequal wings or missing ATM call or put.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
