---
rank: 69
slug: call-ratio-backspread
title: "Call Ratio Backspread"
asset_class: "options"
style: "strongly bullish / long convexity"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 069. Call Ratio Backspread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 69 of 101 |
| Why it sits here | Standard ratio for a squeeze: short fewer near-ATM calls, long more OTM calls. |
| Aliases | — |
| Asset class | options |
| Style | strongly bullish / long convexity |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short $N_S$ near-ATM calls $K_1$ and long $N_L > N_S$ OTM calls $K_2 > K_1$. Typical ratios $2\times 1$ or $3\times 2$. Strongly bullish capital-gain: unlimited upside past the upper break-even, with a loss valley between the strikes.

You are betting on a squeeze through $S^\ast_{\mathrm{up}}$, or — if the package is a credit — on a quiet tape that lets both calls die. You are not betting on a moderate rally to $K_2$. That is the loss valley: shorts fully in the money, longs not yet paying. You are also not running a call credit spread; there are extra longs, so the upside slope is positive.

The typical user wants convexity on a breakout without paying a full OTM call package. Horizon is a single expiry. Prefer a small credit so $H<0$. Refuse $N_L \le N_S$: that would be the front-spread in `071`, which has unlimited *loss* on a squeeze.

Size off $L_{\max}$ at $K_2$, not off the credit. Enter longs first if you must leg. Do not reverse the ratio.

## 2. First principles

Two listed call strikes, same expiry, **more longs than shorts**. The long OTM package pays $N_L(S_T-K_2)_+$. The short near-ATM package pays $-N_S(S_T-K_1)_+$. Subtract net premium paid $H$ ($H<0$ is a credit):

$$
f_T = N_L (S_T - K_2)_+ - N_S (S_T - K_1)_+ - H
$$

The extra longs are the whole point: $N_L-N_S>0$ makes the slope positive above $K_2$. $H$ is a parallel shift. A credit ($H<0$) pays when both calls expire worthless; a debit ($H>0$) loses $H$ on a quiet tape and adds to the valley. If you set $N_L=N_S$ this collapses toward a vertical and the unlimited upside disappears.

Below $K_1$ both calls are out of the money, so $f_T = -H$. A small credit ($H<0$) therefore pays if the stock goes nowhere.

Between $K_1$ and $K_2$ only the short calls are in the money. P&L falls linearly. The worst print is at $S_T = K_2$, where the shorts are fully in the money and the longs have not started to pay. That is the loss valley:

$$
L_{\max} = N_S(K_2 - K_1) + H
$$

Read this as: each short call is in the money by the strike gap, times $N_S$, plus whatever you paid (or minus the credit). This is the number you size off. A moderate rally to the long strike is the *failure* path, not a “wait for the longs” path. If $H>0$, the debit makes the valley deeper.

Above $K_2$ the extra long calls take over because $N_L - N_S > 0$. Slope is $N_L - N_S > 0$, so profit is unlimited into a squeeze.

That is the whole strategy. You are long convexity on the upside, financed by selling fewer closer-to-the-money calls. The danger is a **moderate** rally to $K_2$, not a melt-up.

**Payoff sketch.** Short 1 at $K_1$, long 2 at $K_2$, small credit. At $S_T=0$ (and anywhere below $K_1$), both calls die and you keep the credit. At $S_T=K_2$, you sit in the valley: $f_T=-L_{\max}$. Far above, extra longs dominate and $f_T$ rises without bound past $S^\ast_{\mathrm{up}}$. The sketch is a hole between the strikes and a ray up after the longs kick in.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2$ | short near-ATM call strike, long OTM call strike |
| $N_S$ | number of short $K_1$ calls |
| $N_L$ | number of long $K_2$ calls, $N_L > N_S$ |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Default example: short 1 call $K_1$, long 2 calls $K_2$. Refuse $N_L \le N_S$.

## 4. Mathematics

### 4.1 Premium

Prefer a small credit so $H<0$. Then $f_T=-H>0$ if both calls expire worthless. A debit ($H>0$) still has unlimited upside but loses $H$ if spot goes nowhere. Reject structures where $L_{\max}$ at $K_2$ exceeds a caller cap; a “cheap” debit that deepens the valley is not a bargain.

### 4.2 Terminal payoff

$$
f_T = N_L (S_T - K_2)_+ - N_S (S_T - K_1)_+ - H
$$

Same identity as in first principles; this is what `payoff` implements. Grid tests must hit the valley at $K_2$ and the positive slope above it. Swapping $N_L$ and $N_S$ silently turns this into `071`.

### 4.3 Break-evens

When $H<0$, a lower break-even sits in the loss valley (above $K_1$):

$$
S^\ast_{\mathrm{down}} = K_1 - \frac{H}{N_S} \qquad (H<0)
$$

Because $H$ is negative, $-H/N_S$ is positive and this print is above $K_1$. Below $K_1$ a credit is already profit, so the lower break-even is where the falling valley crosses zero again. If $H\ge 0$ this formula is not used: there is no profit region below $K_1$.

The upper break-even, above $K_2$, is where the extra longs have earned back the valley:

$$
S^\ast_{\mathrm{up}} = \frac{N_L K_2 - N_S K_1 + H}{N_L - N_S}
$$

Unlimited upside only beyond $S^\ast_{\mathrm{up}}$. A squeeze that stops between $K_2$ and $S^\ast_{\mathrm{up}}$ is still a loss. $H$ in the numerator moves the hurdle: a debit pushes $S^\ast_{\mathrm{up}}$ further away.

### 4.4 Max profit and loss

$$
P_{\max} = \text{unlimited}
$$

There is no short call above $K_2$. Do not report a cap. Risk systems that require a finite $P_{\max}$ should store a sentinel, not invent a number.

Maximum loss at $S_T = K_2$:

$$
L_{\max} = N_S(K_2 - K_1) + H
$$

If $H<0$, the credit reduces $L_{\max}$. If $H>0$, the debit adds to it. This is the only finite extremum that matters for sizing. Flattening “because the longs will catch up” while sitting at $K_2$ is optional; the identity says this is the worst expiry print.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. Delta-hedging turns this into a long-gamma squeeze book; the expiry valley at $K_2$ is no longer the P&L. Carry $\Delta, \Gamma, \Theta, \nu$ separately. Unhedged, a grind toward $K_2$ into expiry is theta and short gamma on the near-ATM shorts.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed calls at two strikes, same expiry. The long $K_2$ wing needs enough open interest for $N_L$ contracts. Extra size sits in the OTM long; if that wing is thin, the ratio cannot be the default $2:1$.
2. **Strikes and ratio.** $K_1$ ATM, $K_2$ 5–15% OTM, $K_2 > K_1$. Set $N_L:N_S = 2:1$ or $3:2$. Refuse $N_L \le N_S$. The refuse is what keeps this a backspread.
3. **Legs.** Sell $N_S$ calls $K_1$, buy $N_L$ calls $K_2$. Buy the longs first if the exchange will not take a ratio ticket.
4. **Premium.** Compute $H$. Prefer $H<0$. Reject if $L_{\max} = N_S(K_2-K_1)+H$ exceeds a caller cap. The cap is the valley, not the credit.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}$ (only if $H<0$), $S^\ast_{\mathrm{up}}$, $P_{\max}$ unlimited, $L_{\max}$. Missing the $H<0$ branch on $S^\ast_{\mathrm{down}}$ will invent a fake lower break-even on a debit structure.
6. **Blotter.** Emit a ratio-backspread intent. Do not route live orders.
7. **Hold.** The design is a squeeze through $S^\ast_{\mathrm{up}}$. A grind to $K_2$ is the failure; flatten rather than “wait for the longs.” Waiting at the valley is how the identity’s worst case is realized.

## 6. Execution protocol

- Prefer a small credit ($H<0$) so the trade pays if the stock goes nowhere **or** explodes up. A debit still works as a squeeze bet but loses on a quiet tape as well as in the valley.
- The danger zone is a moderate rally to $K_2$. Size off $L_{\max}$, not off the credit. Sizing off credit is how a $2\times 1$ looks “cheap” and then prints the strike gap.
- Enter as one ratio ticket when the exchange supports it; otherwise buy the $N_L$ longs first, then sell $N_S$. Selling first is $N_S$ naked near-ATM calls.
- Do not convert this into a front-spread by reversing the ratio. That swap is `071` and the squeeze becomes unlimited loss.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **two call strikes**
- Contract multiplier for scaling $N_L$, $N_S$
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the short $K_1$ calls

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them. Delay-0 mids for $H$ are research-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $N_L:N_S$ | $2:1$ or $3:2$ | must have $N_L > N_S$ |
| $K_1$ | ATM | short calls |
| $K_2$ | 5–15% OTM | long calls, $K_2 > K_1$ |
| tenor | 1 week to 3 months | same expiry |
| $H$ | small credit preferred | $H<0$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.call_ratio_backspread` with:

1. `legs(spec) -> list[Leg]` — short $N_S$ calls $K_1$, long $N_L$ calls $K_2$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down` (if $H<0$), `S*_up`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_2 > K_1$, $N_L > N_S$; refuse `n_long <= n_short`; check $L_{\max}$ on a grid at $S_T=K_2$.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Valley at $K_2$.** Max loss sits between the strikes. Unlimited upside only beyond $S^\ast_{\mathrm{up}}$. A grind from ATM to the long strike — a common “right direction, not enough” tape — is the concrete failure.
- **Assignment.** Short near-ATM American calls into a dividend. Assignment can turn the book into extra short stock versus OTM longs that have not paid yet.
- **Debit structure.** If $H>0$, a quiet tape loses the debit as well as any valley. Do not advertise those as “two ways to win.”
- **Wing liquidity.** $N_L > N_S$ concentrates size in the OTM long. A backtest that assumes the wing fills at mid will understate $H$ and the valley.
- **Ratio mix-up.** Implementing $N_L < N_S$ by accident is unlimited upside *risk*, not this file.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $N_L(S_T-K_2)_+ - N_S(S_T-K_1)_+ - H$.
- At $S_T=K_2$, $f_T = -L_{\max} = -N_S(K_2-K_1)-H$.
- For $H<0$, $f_T(S^\ast_{\mathrm{down}})=0$; always $f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject $N_L \le N_S$ or $K_2 \le K_1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
