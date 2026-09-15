---
rank: 68
slug: long-put-butterfly
title: "Long Put Butterfly"
asset_class: "options"
style: "sideways / debit"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 068. Long Put Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 68 of 101 |
| Why it sits here | Put-wing butterfly. Same pin thesis as the call butterfly; sometimes cheaper when skew is steep. |
| Aliases | — |
| Asset class | options |
| Style | sideways / debit |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long one OTM put $K_1$, short two ATM puts $K_2$, long one ITM put $K_3$, with equal spacing $\kappa = K_3 - K_2 = K_2 - K_1$. Quantity ratio $+1/-2/+1$. Net debit. The bet is that $S_T$ pins $K_2$.

You are betting that spot finishes near the body. You are not betting on a crash: outside the wings you lose the debit $D$. You are not running a short straddle; the wings cap both tails. Put-call parity says this is the same butterfly as the call version on the same strikes, up to a bond; the listed put package can still be cheaper when put skew is steep, which is why this file exists beside `041`.

The typical user wants a cheap defined-risk pin. Horizon is a single expiry, usually 1 week to 3 months. If the ATM body cannot lift two short contracts, skip: the $-2$ leg is the fill risk. Reject $D \ge \kappa$; a butterfly that cannot profit at the pin is not this trade.

Enter as one ticket. Legging the body unhedged is two short ATM puts. Pin at $K_2$ is both the thesis and the operational assignment risk.

## 2. First principles

Three listed puts, same expiry, quantity ratio $1:2:1$. The long wings pay $(K_1-S_T)_+$ and $(K_3-S_T)_+$. The short body pays $-2(K_2-S_T)_+$. Subtract the debit $D$:

$$
f_T = (K_1 - S_T)_+ + (K_3 - S_T)_+ - 2(K_2 - S_T)_+ - D
$$

This is the whole expiry map. The $+1/-2/+1$ pattern is what makes the linear terms cancel outside the wings. A $+1/-1/+1$ or a broken ratio is a different fly. $D$ is a parallel shift: it lowers the peak and moves the break-evens inward. Omit $D$ and every metric is optimistic.

Equal spacing means

$$
\kappa = K_3 - K_2 = K_2 - K_1
$$

Equal $\kappa$ is why the closed break-evens and $P_{\max}=\kappa-D$ hold. A broken wing (unequal spacing) still has a peak near the body, but this file’s $S^\ast$ formulas are then wrong. Require equal spacing in `validate`. $\kappa$ is also the max intrinsic you can keep at the pin before subtracting $D$.

Region by region:

- $S_T \le K_1$: all three puts are in the money, so the linear terms cancel to $K_1 + K_3 - 2K_2 = 0$ and $f_T = -D$.
- $K_1 < S_T < K_2$: only $K_2$ and $K_3$ are in the money, and $f_T$ rises linearly through a lower break-even.
- $S_T = K_2$: the body is at the money and the peak is $\kappa - D$.
- $K_2 < S_T < K_3$: only the ITM wing $K_3$ remains, and $f_T$ falls through an upper break-even.
- $S_T \ge K_3$: all puts expire worthless and $f_T = -D$.

You are not betting on a crash. You are betting that spot finishes near $K_2$. Put-call parity says this is the same butterfly as the call version on the same strikes, up to a bond; the listed put package can still be cheaper when put skew is steep.

**Payoff sketch.** Equal wings, debit $D<\kappa$. At $S_T=0$ (through the OTM wing), $f_T=-D$. At $S_T=K_2$, $f_T=\kappa-D$ (peak). Far above $K_3$, every put is dead and $f_T=-D$ again. The sketch is a tent: lose the debit in both tails, keep $\kappa-D$ only if you pin the body.

That is the whole strategy. Everything below is kinks, sizing, and not looking ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2 < K_3$ | OTM, ATM, ITM put strikes |
| $\kappa$ | wing spacing, $\kappa = K_2-K_1 = K_3-K_2$ |
| $(x)_+$ | $\max(x,0)$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Quantity ratio $+1/-2/+1$ puts. Same expiry.

## 4. Mathematics

### 4.1 Premium

Net debit $D > 0$. Require $D < \kappa$ or the butterfly cannot profit at the pin. Compute $D$ from wing asks minus body bids. A mid-to-mid debit that is tiny will not survive the two-sided ATM spread on the $-2$ leg.

### 4.2 Terminal payoff

$$
f_T = (K_1 - S_T)_+ + (K_3 - S_T)_+ - 2(K_2 - S_T)_+ - D
$$

Implementation identity: three put settlements plus cash. Tests should evaluate this on a dense $S_T$ grid and match the region-by-region story above. A sign error on the body (short one instead of two) turns this into a broken fly with leftover directional risk.

### 4.3 Break-evens

Lower break-even, in $(K_1, K_2)$:

$$
S^\ast_{\mathrm{down}} = K_1 + D
$$

Between the OTM wing and the body, the fly rises from $-D$ toward $\kappa-D$. It crosses zero $D$ above $K_1$. If $D \ge \kappa$, this break-even would sit at or beyond $K_2$ and the tent never goes positive — that is why $D<\kappa$ is required.

Upper break-even, in $(K_2, K_3)$:

$$
S^\ast_{\mathrm{up}} = K_3 - D
$$

Symmetric on the ITM side: the remaining $K_3$ put gives back the peak until P&L hits zero $D$ below $K_3$. Outside $[S^\ast_{\mathrm{down}}, S^\ast_{\mathrm{up}}]$ you lose money at expiry. Fees that inflate $D$ squeeze both break-evens inward.

### 4.4 Max profit and loss

Peak at $S_T = K_2$:

$$
P_{\max} = \kappa - D
$$

At the body the two shorts are ATM (worthless) and the ITM wing is worth $\kappa$. That is the whole prize. You do not make more if spot goes to zero: the OTM wing and the extra short cancel the extra intrinsic.

Outside the wings:

$$
L_{\max} = D
$$

Both tails lose the debit. Defined risk is the point of the wings. If you drop a wing, $L_{\max}$ is no longer $D$.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $D$. $P_{\max}$ / $L_{\max}$ are **expiry** quantities. Delta-hedging replaces them with a Greek book. The body is two short ATM puts: gamma into expiry is the pin risk you *want* if you hold to $T$. Marking only the body and ignoring the wings will look like a short straddle.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed puts, three strikes with posted bid/ask and open interest on the body (the $-2$ leg). The body is two contracts; if it cannot fill, the fly cannot fill.
2. **Strikes.** Choose ATM body $K_2 \approx S_0$, then $K_1 = K_2 - \kappa$, $K_3 = K_2 + \kappa$ with $\kappa$ one to three listed strikes. Require $K_1 < K_2 < K_3$ and equal spacing. Unequal $\kappa$ invalidates the closed metrics.
3. **Legs.** Buy 1 put $K_1$, sell 2 puts $K_2$, buy 1 put $K_3$, same expiry. Ratio $+1/-2/+1$. This ratio is the butterfly; anything else is a condor or a ratio spread.
4. **Premium.** Compute $D$ from wing asks minus body bids. Reject if $D \ge \kappa$. That reject is the “cannot profit at the pin” gate.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}=K_1+D$, $S^\ast_{\mathrm{up}}=K_3-D$, $P_{\max}=\kappa-D$, $L_{\max}=D$. Risk and tests read these, not a chart.
6. **Blotter.** Enter as one butterfly ticket. Convert to contracts via the multiplier. Do not route live orders. One ticket so the body never sits naked.
7. **Hold.** Expiry pin at $K_2$ is the design. Compare mid to the call butterfly on the same strikes via put-call parity; take the cheaper package. Holding through a move outside the break-evens is how you donate $D$.

## 6. Execution protocol

- Enter as one butterfly (one ticket, net-debit limit). Do not leg the $-2$ body unhedged. A backtest that fills the shorts first and the wings later will show a short-straddle week that this spec does not allow.
- Compare the put butterfly mid to the call butterfly on $K_1,K_2,K_3$. Parity says they differ by a bond; fill the cheaper listed package. Ignoring that comparison is how you overpay for steep put skew.
- Pin at $K_2$ into expiry: you want exercise/assignment to collapse toward a flat book. American names can leave a residual stock position.
- Cap the body by ADV of the ATM put, not by $D$ alone. Small debit, two short ATMs.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **three put strikes**
- Optional: the matching call butterfly quotes for a parity cross-check
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them. Delay-0 mids for $D$ are research-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K_2$ | ATM | body |
| $\kappa$ | one to three listed strikes | equal wings |
| quantity ratio | $+1/-2/+1$ | puts only |
| tenor | 1 week to 3 months | same expiry all legs |
| $D$ | market | must satisfy $D < \kappa$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_put_butterfly` with:

1. `legs(spec) -> list[Leg]` — $+1/-2/+1$ puts at $K_1<K_2<K_3$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down`, `S*_up`, `P_max`, `L_max`, debit flag.
5. `validate(spec)` — $K_1<K_2<K_3$, $K_2-K_1=K_3-K_2=\kappa$, qty $+1/-2/+1$, and $P_{\max}=\kappa-D$, $L_{\max}=D$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Debit.** Lost in full if $S_T$ finishes outside $[S^\ast_{\mathrm{down}}, S^\ast_{\mathrm{up}}]$. A trend week or an earnings gap through a wing is the usual path, not a crash to zero (zero still only loses $D$).
- **Pin at $K_2$.** That is the thesis; it is also assignment/exercise operational risk. Settlement exactly at the body can leave a two-short residual.
- **Body liquidity.** Two short ATM puts dominate the spread cost. Using mids for $D$ makes the fly look cheaper than it fills.
- **Skew.** A steep put smile can make the ITM wing expensive; then the call butterfly on the same strikes may be cheaper. Skipping the parity check is how you buy the expensive package.
- **Unequal $\kappa$.** A broken wing is a different payoff; this file’s break-evens assume equal spacing.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals the sum of listed put intrinsics minus $D$.
- At $S_T=K_2$, $f_T=\kappa-D=P_{\max}$. At $S_T \le K_1$ and $S_T \ge K_3$, $f_T=-D=-L_{\max}$.
- $f_T(S^\ast_{\mathrm{down}})=f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject unequal spacing, wrong quantity ratio, or $K_1 \ge K_2$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
