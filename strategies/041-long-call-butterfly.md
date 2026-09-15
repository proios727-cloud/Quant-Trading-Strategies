---
rank: 41
slug: long-call-butterfly
title: "Long Call Butterfly"
asset_class: "options"
style: "sideways / debit / defined risk"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 041. Long Call Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 41 of 101 |
| Why it sits here | Classic body-and-wings structure. Cheaper defined-risk bet that spot pins $K_2$. |
| Aliases | — |
| Asset class | options |
| Style | sideways / debit / defined risk |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long OTM call $K_1$, short two ATM calls $K_2$, long ITM call $K_3$, equidistant $\kappa = K_2-K_3 = K_1-K_2$. Low-cost debit. Neutral, capital-gain.

You are betting that $S_T$ pins $K_2$. You bought the wings and sold the body so a pin at the body is the whole trade. You are not selling unlimited vol: outside $[K_3,K_1]$ the $+1/-2/+1$ calls cancel and you lose only $D$. You are not running a credit iron butterfly; this file is a debit in calls. Paper labels $K_1$ OTM, $K_2$ ATM, $K_3$ ITM, so numerically $K_3<K_2<K_1$. Do not relabel without flipping the formulas.

Payoff sketch, one fly, ignore financing: at $S_T=0$ all three calls die and $f_T=-D=-L_{\max}$. At $S_T=K_2$ the body is worthless, the ITM wing is worth $\kappa$, the OTM wing is worthless, and $f_T=\kappa-D=P_{\max}$. Far above $K_1$ the three calls cancel to zero intrinsic and $f_T=-D$ again.

## 2. First principles

This file’s strike labels are $K_3 < K_2 < K_1$: $K_3$ is the ITM call, $K_2$ the ATM body, $K_1$ the OTM wing.

A long ITM call at $K_3$ pays

$$
(S_T - K_3)_+
$$

That is the left wing in call space (the lower strike). Below $K_3$ it is zero. Above $K_3$ it rises one-for-one. Alone it is a deep-ITM debit that behaves like stock minus $K_3$.

Two short ATM calls at $K_2$ pay

$$
-2(S_T - K_2)_+
$$

That is the body. The factor of two is load-bearing: one short is a vertical, three shorts is a broken ratio. Above $K_2$ this falls two-for-one, which is what creates the tent peak when combined with the two long wings.

A long OTM call at $K_1$ pays

$$
(S_T - K_1)_+
$$

That is the right wing. It starts paying only after $S_T$ clears $K_1$, which is what stops the two shorts from running. Equal spacing $\kappa$ makes the two wings cancel the body exactly outside the fly.

The wings cost more than the two short ATM calls bring in, so the package is a net debit $D$ at $t=0$. Adding the four pieces is the long call butterfly:

$$
f_T = (S_T-K_1)_+ + (S_T-K_3)_+ - 2(S_T-K_2)_+ - D
$$

$D$ must be less than $\kappa$ or $P_{\max}$ is not positive. $D$ is three strikes of fills, with two lots on the body. Outside $[K_3,K_1]$ the $+1/-2/+1$ calls cancel to zero intrinsic and you lose $D$. At $S_T=K_2$ the body is worthless, the ITM wing is worth $\kappa$, and the OTM wing is worthless, so you earn $\kappa-D$. You bought the wings and sold the body so a pin at $K_2$ is the whole trade.

That is the whole strategy. Everything below is how to keep equal spacing $\kappa$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_3 < K_2 < K_1$ | ITM, ATM, OTM call strikes |
| $\kappa$ | wing width, $K_2-K_3 = K_1-K_2$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Quantity ratio $+1 / -2 / +1$. Same expiry $T$. Structure so $D < \kappa$.

## 4. Mathematics

### 4.1 Terminal payoff

Long $K_1$, short two $K_2$, long $K_3$, net debit $D$:

$$
f_T = (S_T-K_1)_+ + (S_T-K_3)_+ - 2(S_T-K_2)_+ - D
$$

Tent with peak at $K_2$. Tests must keep the factor of two and the label order $K_3<K_2<K_1$. Sketch: $S_T=0$ prints $-D$; at $K_2$ prints $\kappa-D$; far above $K_1$ prints $-D$.

### 4.2 Break-evens

On the ITM side, $f_T=0$ at

$$
S^\ast_{\mathrm{down}} = K_3 + D
$$

Spot must climb through the ITM wing by $D$ before the fly is even flat. If $D$ is a large fraction of $\kappa$, the down-side break-even sits close to $K_2$ and the profitable band is a thin pin.

On the OTM side, $f_T=0$ at

$$
S^\ast_{\mathrm{up}} = K_1 - D
$$

Symmetric. The profitable band is $(K_3+D,\,K_1-D)$, centered on $K_2$ when spacing is equal. A cheap fly ($D\ll\kappa$) has a wide band; an expensive fly is a pin lottery.

### 4.3 Extrema

Maximum profit is the wing width net of the debit, attained at $S_T=K_2$:

$$
P_{\max} = \kappa - D
$$

Exactly at the body. A print a few ticks off $K_2$ nibble this number. Pin friction and American exercise can keep you from collapsing to a flat book at the peak.

Maximum loss is the debit, attained for $S_T \le K_3$ or $S_T \ge K_1$:

$$
L_{\max} = D
$$

Both tails lose the same $D$. That is defined risk. A broken wing (unequal $\kappa$) makes one tail a different number; this file's formula assumes equal spacing.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with three equidistant call strikes around spot. Open interest on the body (two shorts) above a minimum. The body is two lots; that is the fill risk. A missing wing is a ratio spread.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K_2$ ATM. A later print look-aheads $D$ and which strike is the body.
3. **Strikes.** Choose $K_3<K_2<K_1$ with $K_2\approx S_0$ and $K_2-K_3=K_1-K_2=\kappa$. Default $\kappa$: one to three listed strikes. Unequal $\kappa$ is a broken fly; rewrite break-evens before you trade it.
4. **Expiry.** Same $T$ on all three strikes. Mixed expiries are a calendar fly, not this payoff. Short-dated flies are more binary into the body.
5. **Size.** $+1$ at $K_3$, $-2$ at $K_2$, $+1$ at $K_1$. The factor of two is the butterfly. One short is a vertical; three shorts are a ratio.
6. **Premium.** $D$ is the net debit actually paid. Reject if $D \ge \kappa$. A fly that costs the whole width has no $P_{\max}$.
7. **Blotter.** Emit a butterfly intent. Do not route live orders. One ticket keeps the two shorts from going on without both wings.
8. **Hold.** Pin risk at $K_2$ into expiry: you want assignment/exercise to collapse to a flat book. Early exit is a mark of remaining time value on three strikes, not $\kappa-D$.

## 6. Execution protocol

- Enter as a butterfly (one ticket). Do not short two ATM calls without both wings on.
- Paper labels $K_1$ OTM, $K_2$ ATM, $K_3$ ITM, so numerically $K_3 < K_2 < K_1$. Do not relabel to the textbook $K_1<K_2<K_3$ without flipping the formulas.
- Cap lots by ADV on the body.
- American early exercise on the shorts can break the European pin.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| body $K_2$ | ATM | $K_2 \approx S_0$ |
| $\kappa$ | one to three listed strikes | equal wings |
| quantity | $+1/-2/+1$ | $K_3$, $K_2$, $K_1$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_call_butterfly` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_3<K_2<K_1$ and $K_2-K_3=K_1-K_2$; qty $+1/-2/+1$; $P_{\max}=\kappa-D$ and $L_{\max}=D$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Debit lost** if spot finishes outside the wings. A 10% rally through $K_1$ still prints $-D$. The fly is a pin bet, not a "market will not crash" bet.
- **Body liquidity.** The trade is two short ATM options; that is the fill risk. Lifting two ATM offers and hitting two wing bids can make $D$ a large fraction of $\kappa$.
- **Unequal $\kappa$.** A broken wing is a different payoff; this file’s break-evens assume equal spacing. Reporting $P_{\max}=\kappa-D$ with $\kappa$ taken from one wing only is a silent error on the other tail.
- **Pin friction.** Assignment/exercise at $K_2$ may not collapse cleanly on American names. You can be left with a stub stock position into the next open.
- **Label swap.** Relabeling to $K_1<K_2<K_3$ without flipping the formulas puts the ITM wing on the wrong side. Tests on $K_3<K_2<K_1$ exist specifically to stop that.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K_1)_++(S_T-K_3)_+-2(S_T-K_2)_+-D$.
- Break-evens: $f_T(S^\ast_{\mathrm{down}})=f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K_2$, $f_T=\kappa-D=P_{\max}$. For $S_T\le K_3$ or $S_T\ge K_1$, $f_T=-D=-L_{\max}$.
- Reject a spec that violates $K_3<K_2<K_1$, unequal spacing, or qty other than $+1/-2/+1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
