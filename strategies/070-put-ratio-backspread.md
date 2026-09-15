---
rank: 70
slug: put-ratio-backspread
title: "Put Ratio Backspread"
asset_class: "options"
style: "strongly bearish / long convexity"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 070. Put Ratio Backspread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 70 of 101 |
| Why it sits here | Crash convexity package. Standard $2\times 1$ or $3\times 2$ put backspread. |
| Aliases | — |
| Asset class | options |
| Style | strongly bearish / long convexity |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short $N_S$ near-ATM puts $K_1$ and long $N_L > N_S$ OTM puts $K_2 < K_1$. Typical ratios $2\times 1$ or $3\times 2$. Crash convexity: large (finite) profit if $S_T \to 0$, with a loss valley on a moderate selloff to $K_2$.

You are betting on a crash through $S^\ast_{\mathrm{down}}$, or — if $H<0$ — on a quiet tape. You are not betting on a moderate selloff that stops at the long put strike. That stop is the valley: shorts fully in the money, extra longs not yet paying. You are not running a put credit spread; extra longs make the downside slope negative (profit as spot falls) once you are through $K_2$.

The typical user wants crash convexity without paying a full strip of OTM puts. Horizon is one expiry. Prefer a credit. Refuse $N_L \le N_S$: that is the put front-spread in `072`, which *loses* at zero.

Size off $L_{\max}$ at $K_2$, not off credit. $P_{\max}$ at zero is large but finite. Buy the OTM longs first if you must leg; never warehouse $N_S$ naked near-ATM puts into a selloff.

## 2. First principles

Two listed put strikes, same expiry, **more longs than shorts**. The long OTM package pays $N_L(K_2-S_T)_+$. The short near-ATM package pays $-N_S(K_1-S_T)_+$. Subtract net premium paid $H$:

$$
f_T = N_L (K_2 - S_T)_+ - N_S (K_1 - S_T)_+ - H
$$

$N_L>N_S$ is what makes the crash pay. $H$ shifts the whole map. A credit pays when both puts die (spot stays above $K_1$). Swapping the counts turns this into a front-spread with a hole at zero. Implementation must refuse `n_long <= n_short`.

Above $K_1$ both puts are out of the money, so $f_T = -H$. A credit ($H<0$) therefore pays on a quiet tape.

Between $K_2$ and $K_1$ only the short puts are in the money. P&L falls as spot drops. The worst print is at $S_T = K_2$, where the shorts are fully in the money and the extra longs have not started to pay:

$$
L_{\max} = N_S(K_1 - K_2) + H
$$

Each short put is in by the strike gap; the longs at $K_2$ are still worthless at that print. This is the moderate-selloff failure. Size off it. A debit ($H>0$) deepens the hole. Flattening here is optional; expiry will print this number if you hold.

Below $K_2$ the extra long puts take over. At $S_T = 0$ every put is worth its strike, so profit is large but finite:

$$
P_{\max} = N_L K_2 - N_S K_1 - H
$$

Stock cannot go below zero, so there is no unlimited put profit. Gap-to-zero still has to clear and settle; $P_{\max}$ is an accounting cap, not a promise that the OTM wing traded through the gap. If $N_L K_2 < N_S K_1$ the crash would not even pay — that is a bad strike/ratio mix and should fail validation against this closed form.

That is the whole strategy. You are long crash convexity, financed by selling fewer closer-to-the-money puts. The danger is a **moderate** selloff to $K_2$, not a collapse to zero.

**Payoff sketch.** Short 1 at $K_1$, long 2 at $K_2<K_1$, small credit. At $S_T$ far above $K_1$, both puts die and you keep the credit. At $S_T=K_2$, valley: $f_T=-L_{\max}$. At $S_T=0$, $f_T=P_{\max}=N_L K_2-N_S K_1-H$, large and finite. The sketch is a hole on the way down and a high floor at zero.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_2 < K_1$ | long OTM put strike, short near-ATM put strike |
| $N_S$ | number of short $K_1$ puts |
| $N_L$ | number of long $K_2$ puts, $N_L > N_S$ |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Default example: short 1 put $K_1$, long 2 puts $K_2 < K_1$. Refuse $N_L \le N_S$.

## 4. Mathematics

### 4.1 Premium

Credit-structured backspreads ($H<0$) profit from a crash **or** from a quiet tape. They lose on a moderate selloff to $K_2$. A debit still has crash convexity but loses on a quiet tape as well. Prefer $H<0$ only after $L_{\max}$ clears a cap.

### 4.2 Terminal payoff

$$
f_T = N_L (K_2 - S_T)_+ - N_S (K_1 - S_T)_+ - H
$$

This is what `payoff` implements. Grid from $0$ to $3S_0$ must recover $P_{\max}$ at zero and $-L_{\max}$ at $K_2$. A strike swap $K_2 \ge K_1$ is invalid: the “OTM” longs would not be below the shorts.

### 4.3 Break-evens

When $H<0$, an upper break-even sits in the loss valley (below $K_1$):

$$
S^\ast_{\mathrm{up}} = K_1 + \frac{H}{N_S} \qquad (H<0)
$$

$H<0$ so this print is below $K_1$. Above $K_1$ a credit is already profit. The upper break-even is where the falling valley crosses zero. Do not emit this key on a debit structure.

The lower break-even, below $K_2$, is where the extra longs have earned back the valley:

$$
S^\ast_{\mathrm{down}} = \frac{N_L K_2 - N_S K_1 - H}{N_L - N_S}
$$

A crash that stops between $K_2$ and $S^\ast_{\mathrm{down}}$ is still a loss. A debit pushes $S^\ast_{\mathrm{down}}$ lower (harder hurdle). This is the analogue of $S^\ast_{\mathrm{up}}$ in `069`.

### 4.4 Max profit and loss

At $S_T = 0$:

$$
P_{\max} = N_L K_2 - N_S K_1 - H
$$

Finite. Tests should check this closed form, not “unlimited.” If the formula is negative, the ratio/strikes do not pay at zero.

At $S_T = K_2$:

$$
L_{\max} = N_S(K_1 - K_2) + H
$$

$P_{\max}$ is large but finite. Stock cannot go below zero. $L_{\max}$ is the moderate-down hole you actually size. Credit reduces it; debit increases it.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. Delta-hedging replaces the expiry valley with a long-put-gamma book. Carry $\Delta, \Gamma, \Theta, \nu$ separately. American short puts have assignment cascades into a selloff: you can be long stock from the shorts while the OTM longs are still open.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed puts at two strikes, same expiry. The long $K_2$ wing must lift $N_L$ contracts. Crash convexity is concentrated in that wing; a thin put tail cannot carry a $2:1$.
2. **Strikes and ratio.** $K_1$ near ATM, $K_2$ 5–15% OTM, $K_2 < K_1$. Set $N_L:N_S = 2:1$ or $3:2$. Refuse $N_L \le N_S$. That refuse is the backspread gate.
3. **Legs.** Sell $N_S$ puts $K_1$, buy $N_L$ puts $K_2$. Buy longs first if you must leg.
4. **Premium.** Compute $H$. Prefer $H<0$. Reject if $L_{\max}$ exceeds a caller cap. The cap is the valley at $K_2$.
5. **Metrics.** Store $S^\ast_{\mathrm{up}}$ (if $H<0$), $S^\ast_{\mathrm{down}}$, $P_{\max}$, $L_{\max}$. Include $P_{\max}$ as a finite number, not a sentinel.
6. **Blotter.** Emit a put-backspread intent. Do not route live orders.
7. **Hold.** A crash through $S^\ast_{\mathrm{down}}$ is the design. A grind to $K_2$ is the failure. Do not add shorts into the valley.

## 6. Execution protocol

- Credit-structured backspreads profit from a crash or from a quiet tape; they lose on a moderate selloff to $K_2$. Advertising only the two winning regions is how the valley gets forgotten.
- Size off $L_{\max}$, not off collected credit.
- Buy the $N_L$ OTM puts first if you must leg; never warehouse $N_S$ naked near-ATM shorts against a crash.
- $P_{\max}$ at zero is the accounting cap; gap-to-zero still has to clear and settle. A backtest that interpolates through a halt will book $P_{\max}$ the live tape never paid.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **two put strikes**
- Contract multiplier for $N_L$, $N_S$
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the short $K_1$ puts

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $N_L:N_S$ | $2:1$ or $3:2$ | must have $N_L > N_S$ |
| $K_1$ | near ATM | short puts |
| $K_2$ | 5–15% OTM | long puts, $K_2 < K_1$ |
| tenor | 1 week to 3 months | same expiry |
| $H$ | small credit preferred | $H<0$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.put_ratio_backspread` with:

1. `legs(spec) -> list[Leg]` — short $N_S$ puts $K_1$, long $N_L$ puts $K_2 < K_1$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_up` (if $H<0$), `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_2 < K_1$, $N_L > N_S$; $P_{\max}$ at $S_T=0$ and $L_{\max}$ at $S_T=K_2$ match the closed forms on a grid.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Valley at $K_2$.** Max loss in the moderate-down region. A 8–12% selloff that “almost” crashes is the usual way this book loses, not a bounce.
- **Finite crash profit.** $P_{\max}$ is large but finite (stock at 0). Treating it as unlimited will mis-state risk versus `069`.
- **Assignment cascade** on short American puts. Share delivery is not offset 1:1 by extra OTM longs.
- **Debit structure.** If $H>0$, a quiet tape loses the debit.
- **Wing liquidity.** $N_L$ in the put tail is the fill. Mid-based $H$ understates the valley.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $N_L(K_2-S_T)_+ - N_S(K_1-S_T)_+ - H$.
- At $S_T=0$, $f_T = P_{\max} = N_L K_2 - N_S K_1 - H$.
- At $S_T=K_2$, $f_T = -L_{\max} = -N_S(K_1-K_2)-H$.
- Reject $N_L \le N_S$ or $K_2 \ge K_1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
