---
rank: 75
slug: short-call-butterfly
title: "Short Call Butterfly"
asset_class: "options"
style: "long volatility / credit / small reward"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 075. Short Call Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 75 of 101 |
| Why it sits here | Short the body, long the wings inverted vs the long butterfly. Used as a cheap long-vol flyer; reward $\ll$ short straddle. |
| Aliases | — |
| Asset class | options |
| Style | long volatility / credit / small reward |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short one ITM call $K_1$, long two ATM calls $K_2$, short one OTM call $K_3$, with equal spacing $\kappa$. Quantity ratio $-1/+2/-1$. Net credit. This is the long-vol / anti-pin inverse of the long call butterfly: small income if spot finishes **outside** the wings, max loss if spot pins $K_2$.

You are betting that spot *leaves* $K_2$. You are long the ATM body, so this is a long-vol / anti-pin trade, not a pin sale. You are not running a long straddle: you sold the wings, so a large move pays only the credit $C$, while a pin loses $\kappa-C$. Do not mix it up with `041`, which wants the pin.

The typical user wants a cheap long-vol flyer with defined loss. Horizon is one expiry. Require $C<\kappa$. If $C\ge\kappa$ the quotes are not a coherent short butterfly; reject. Enter as one ticket. Cap the body by ATM ADV. Reward is small versus a long straddle — that is the design, not a bug to “fix” by dropping a wing.

## 2. First principles

Three listed calls, same expiry, quantity ratio $1:2:1$ with the **body long**. The two long ATM calls pay $2(S_T-K_2)_+$. The short wings pay $-(S_T-K_1)_+$ and $-(S_T-K_3)_+$. Add the credit $C$ received:

$$
f_T = 2(S_T - K_2)_+ - (S_T - K_1)_+ - (S_T - K_3)_+ + C
$$

This is minus a long call butterfly, with premium signed as a credit. The $+2$ body is why a pin hurts and a move helps, up to the wings. $C$ is a parallel lift. A sign error on the body (short two instead of long two) silently implements `041`.

Equal spacing means

$$
\kappa = K_2 - K_1 = K_3 - K_2
$$

Equal $\kappa$ is why the linear terms cancel outside the wings and why $L_{\max}=\kappa-C$. A broken wing invalidates the closed metrics. $\kappa$ is also the intrinsic the short ITM call is worth at a $K_2$ pin.

This is minus a long call butterfly, with premium signed as a credit $C$ instead of a debit $D$. Region by region:

- $S_T \le K_1$: every call expires out of the money, so $f_T = C$.
- $S_T \ge K_3$: every call expires in the money; equal spacing cancels the linear terms and $f_T = C$.
- $S_T = K_2$: the long body is at the money and the short $K_1$ call is worth $\kappa$, so $f_T = C - \kappa$. That is the pin loss.

You are long the ATM, so this is a long-vol / anti-pin trade. Do not mix it up with the long butterfly, which wants the pin.

**Payoff sketch.** Equal wings, credit $C<\kappa$. At $S_T=0$ (below $K_1$), all calls die: $f_T=C$ (keep the credit). At $S_T=K_2$, pin loss $f_T=C-\kappa=-L_{\max}$. Far above $K_3$, all calls in the money cancel to $f_T=C$ again. The sketch is an inverted tent: small pay in both tails, hole at the body.

That is the whole strategy. Small credit, defined loss $\kappa - C$.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2 < K_3$ | short ITM, long ATM, short OTM call strikes |
| $\kappa$ | wing spacing, $\kappa = K_2-K_1 = K_3-K_2$ |
| $(x)_+$ | $\max(x,0)$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Quantity ratio $-1/+2/-1$ calls. Same expiry. Require $C < \kappa$.

## 4. Mathematics

### 4.1 Premium

Net credit $C > 0$. If $C \ge \kappa$ the short butterfly cannot lose, which means the quotes are not a coherent butterfly; reject. Convexity in strike makes a long butterfly a debit, so this inverse is a credit. Compute $C$ from wing bids minus body asks. Mid-to-mid credit overstates $P_{\max}$ and understates $L_{\max}$.

### 4.2 Terminal payoff

$$
f_T = 2(S_T - K_2)_+ - (S_T - K_1)_+ - (S_T - K_3)_+ + C
$$

Implementation identity. Grid tests must show $C$ outside the wings and $C-\kappa$ at $K_2$. Note $+C$ at the end, not $-D$: this file is a credit structure.

### 4.3 Break-evens

Lower break-even, in $(K_1, K_2)$:

$$
S^\ast_{\mathrm{down}} = K_1 + C
$$

Inside the wings P&L falls from $C$ toward $C-\kappa$. It crosses zero $C$ above $K_1$. If $C\ge\kappa$ this crossing would not happen as a loss region — another reason to reject.

Upper break-even, in $(K_2, K_3)$:

$$
S^\ast_{\mathrm{up}} = K_3 - C
$$

Outside $[S^\ast_{\mathrm{down}}, S^\ast_{\mathrm{up}}]$ the credit is kept. Inside, the pin costs. Fees that reduce $C$ widen the loss region (break-evens move out). That is the opposite of a long butterfly, where fees squeeze the profit tent.

### 4.4 Max profit and loss

Outside the wings:

$$
P_{\max} = C
$$

At $S_T = K_2$:

$$
L_{\max} = \kappa - C
$$

Small reward, defined loss. A melt-up does not pay like a long straddle because you sold $K_3$. A pin does not pay like a long butterfly because you are long the body. Both facts are load-bearing. Size off $L_{\max}$, not off $C$.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids plus initial $C$ (equivalently minus $H=-C$). $P_{\max}$ / $L_{\max}$ are **expiry** quantities. You are long ATM gamma: theta is a drag if nothing happens. Carry $\Delta, \Gamma, \Theta, \nu$ if you hedge. Holding into a quiet expiry is how you realize the pin hole while theta eats the mark.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed calls, three strikes. The $+2$ ATM body must have two-sided size. You are buying two ATMs; if that line is thin, skip.
2. **Strikes.** ATM body $K_2 \approx S_0$, equal $\kappa$, $K_1 < K_2 < K_3$. Unequal spacing breaks $L_{\max}=\kappa-C$.
3. **Legs.** Sell 1 call $K_1$, buy 2 calls $K_2$, sell 1 call $K_3$. Ratio $-1/+2/-1$. This ratio is the inverse fly; $+1/-2/+1$ is `041`.
4. **Premium.** Sell the wings, buy two bodies. Convexity in strike makes a long butterfly a debit, so this short butterfly is a credit $C>0$. Reject if $C \ge \kappa$. Incoherent quotes, not a free lunch.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}=K_1+C$, $S^\ast_{\mathrm{up}}=K_3-C$, $P_{\max}=C$, $L_{\max}=\kappa-C$. Risk reads $L_{\max}$, not $C$.
6. **Blotter.** Enter as one short butterfly ticket. Do not route live orders. Legging the $+2$ body without wings is a long straddle-ish inventory.
7. **Hold.** You want a move **away** from $K_2$. Pin is the failure. Flatten if you no longer want to pay theta for a move that is not arriving.

## 6. Execution protocol

- This is long the ATM, so it is a long-vol / anti-pin trade. Do not mix up with the long butterfly. Broker names sometimes invert long/short; match the legs.
- Enter as one ticket. Legging the $+2$ body without the short wings is a long straddle-ish inventory.
- Reward is small versus a long straddle: you sold the wings, so a large move pays only $C$, while a pin loses $\kappa-C$. Do not “fix” that by dropping a wing in the backtest.
- Cap the body by ATM ADV.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **three call strikes**
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the short wings

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K_2$ | ATM | long body |
| $\kappa$ | equal wings | $K_2-K_1=K_3-K_2$ |
| quantity ratio | $-1/+2/-1$ | calls only |
| tenor | 1 week to 3 months | same expiry |
| $C$ | market | must satisfy $C < \kappa$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_call_butterfly` with:

1. `legs(spec) -> list[Leg]` — $-1/+2/-1$ calls at $K_1<K_2<K_3$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive), equal to $C$ on a valid short butterfly.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down`, `S*_up`, `P_max`, `L_max`, credit flag.
5. `validate(spec)` — equal $\kappa$, qty $-1/+2/-1$, $P_{\max}=C$, $L_{\max}=\kappa-C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Pin at $K_2$.** Max loss $\kappa-C$. That is the anti-thesis of the long butterfly. Settlement at the body with two long ATMs is also operational pin risk.
- **Small credit.** $P_{\max}=C$ is a poor payoff for being right about a large move; you sold the wings. A backtest that compares this to a long straddle without noting the cap will look like a bad vol purchase, which it is by design.
- **Theta.** Long ATM gamma costs if nothing happens before expiry. Quiet tape realizes the hole.
- **Wing assignment** on the short ITM $K_1$ call. You can be short stock versus two long ATMs that have not fully offset.
- **Naming clash.** Implementing $+1/-2/+1$ because the screen said “short butterfly” inverts the payoff.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $2(S_T-K_2)_+ - (S_T-K_1)_+ - (S_T-K_3)_+ + C$.
- At $S_T=K_2$, $f_T = C-\kappa = -L_{\max}$. At $S_T \le K_1$ and $S_T \ge K_3$, $f_T=C=P_{\max}$.
- $f_T(S^\ast_{\mathrm{down}})=f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject unequal spacing or quantity ratio other than $-1/+2/-1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
