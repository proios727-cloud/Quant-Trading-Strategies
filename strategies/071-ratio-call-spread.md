---
rank: 71
slug: ratio-call-spread
title: "Ratio Call Spread"
asset_class: "options"
style: "neutral to bearish / income if credit"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 071. Ratio Call Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 71 of 101 |
| Why it sits here | Front-spread: long fewer ITM calls, short more ATM calls. Common market-maker inventory hedge; opposite of the backspread. |
| Aliases | call front-spread |
| Asset class | options |
| Style | neutral to bearish / income if credit |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short $N_S$ near-ATM calls $K_1$ and long $N_L < N_S$ ITM calls $K_2$, with $K_1 > K_2$. Typical ratios $1\times 2$ or $2\times 3$. This is the opposite of the call ratio backspread: unlimited upside risk, defined peak between the strikes.

You are betting that spot finishes near $K_1$, or at least does not squeeze through $S^\ast_{\mathrm{up}}$. You are selling upside convexity. You are not running a defined-risk call spread: extra shorts make the slope negative above $K_1$ with no cap. Prefer a credit, or convert to a call butterfly by buying a further OTM call.

The typical user is a market-maker inventory hedge, not a retail income default. Horizon is one expiry. Refuse $N_L \ge N_S$; that would be `069` or a vertical. Size off the rally tail, not off $P_{\max}$. Flatten on a grind through $S^\ast_{\mathrm{up}}$. Do not “wait for mean reversion” against unlimited calls.

## 2. First principles

Two listed call strikes, same expiry, **more shorts than longs**. The long ITM package pays $N_L(S_T-K_2)_+$. The short near-ATM package pays $-N_S(S_T-K_1)_+$. Subtract net premium paid $H$:

$$
f_T = N_L (S_T - K_2)_+ - N_S (S_T - K_1)_+ - H
$$

The formula looks like `069`; the inequality $N_S>N_L$ flips the economics. Slope above $K_1$ is $N_L-N_S<0$. $H$ is a shift. A credit cushions the peak and the quiet-tape region; a debit starts from a hole and still has unlimited loss. Implementation must refuse `n_long >= n_short`.

Below $K_2$ both calls are out of the money (the long is ITM at inception but expires OTM if $S_T < K_2$), so $f_T = -H$. A debit ($H>0$) therefore needs spot to climb through a lower break-even.

Between $K_2$ and $K_1$ only the longs are in the money. P&L rises to a peak at $S_T = K_1$:

$$
P_{\max} = N_L(K_1 - K_2) - H
$$

That peak is the *best* case, not a coupon you keep if spot goes further. Each long call is in by the strike gap; the shorts at $K_1$ are still worthless at that print. If $P_{\max}\le 0$, reject: you paid more than the gap can return.

Above $K_1$ the extra short calls take over because $N_S - N_L > 0$. Slope is $N_L - N_S < 0$, so loss is unlimited into a squeeze.

That is the whole strategy. You are selling upside convexity. It is the dangerous twin of `069`. Prefer a credit, or convert to a call butterfly by buying a further OTM call.

**Payoff sketch.** Long 1 ITM at $K_2$, short 2 ATM at $K_1$. At $S_T=0$ (below $K_2$), both expire worthless: $f_T=-H$ (keep a credit, lose a debit). At $S_T=K_1$, peak $P_{\max}$. Far above, extra shorts dominate and $f_T\to-\infty$ past $S^\ast_{\mathrm{up}}$. The sketch is a tent with the right wall missing.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_2 < K_1$ | long ITM call strike, short near-ATM call strike |
| $N_L$ | number of long $K_2$ calls |
| $N_S$ | number of short $K_1$ calls, $N_S > N_L$ |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast_{\mathrm{down}}$, $S^\ast_{\mathrm{up}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Default example: long 1 ITM call $K_2$, short 2 ATM calls $K_1 > K_2$. Refuse $N_L \ge N_S$.

## 4. Mathematics

### 4.1 Premium

Only as a credit, or with a hard stop, because of unlimited upside. $H>0$ still has a peak at $K_1$ but starts from a hole. A credit does not cap the rally; it only lifts the whole map. If $P_{\max}$ is not positive after $H$, reject.

### 4.2 Terminal payoff

$$
f_T = N_L (S_T - K_2)_+ - N_S (S_T - K_1)_+ - H
$$

Same algebraic family as the backspread; validate the counts. Grid tests must show a peak at $K_1$ and a negative slope after. A further OTM long call is a different spec (butterfly) and is not in this identity unless you add the leg.

### 4.3 Break-evens

When $H>0$, a lower break-even sits above $K_2$:

$$
S^\ast_{\mathrm{down}} = K_2 + \frac{H}{N_L} \qquad (H>0)
$$

A debit needs the longs to earn $H$ before P&L goes positive. If $H\le 0$, below $K_2$ you already keep the credit (or zero), so this key is omitted. Do not apply this formula to a credit structure.

The upper break-even, above $K_1$, is where the extra shorts have given back the peak:

$$
S^\ast_{\mathrm{up}} = \frac{N_S K_1 - N_L K_2 - H}{N_S - N_L}
$$

Beyond this print the extra shorts have eaten the peak and more. Flatten here; the identity has no second chance. A debit pulls $S^\ast_{\mathrm{up}}$ closer (less room).

### 4.4 Max profit and loss

Peak at $S_T = K_1$:

$$
P_{\max} = N_L(K_1 - K_2) - H
$$

$$
L_{\max} = \text{unlimited}
$$

Store unlimited as a sentinel. Risk that looks only at $P_{\max}$ will treat this as a defined-risk income trade. It is not. A buyout or squeeze through $K_1$ is the concrete path.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. Delta-hedging does not cap the short-call tail. Carry $\Delta, \Gamma, \Theta, \nu$ separately. A further OTM long call converts this into a butterfly and replaces $L_{\max}$ with a defined number. Until that wing is on, mark-to-market can look fine the day before a gap-up.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed calls at two strikes, same expiry. The short $K_1$ line must absorb $N_S$ contracts. Extra risk sits in those shorts; thin ATM calls cannot carry a $1:2$.
2. **Strikes and ratio.** $K_2$ ITM, $K_1$ near ATM, $K_1 > K_2$. Set $N_L:N_S = 1:2$ or $2:3$. Refuse $N_L \ge N_S$. That refuse is the front-spread gate.
3. **Legs.** Buy $N_L$ calls $K_2$, sell $N_S$ calls $K_1$. Longs first if you must leg.
4. **Premium.** Prefer $H<0$. If $H>0$, require a documented stop. Compute $P_{\max} = N_L(K_1-K_2)-H$ and reject if it is not positive. The reject stops a debit that cannot even pay at the peak.
5. **Metrics.** Store $S^\ast_{\mathrm{down}}$ (if $H>0$), $S^\ast_{\mathrm{up}}$, $P_{\max}$, $L_{\max}$ unlimited. Document unlimited explicitly so a downstream risk tool cannot assume a cap.
6. **Blotter.** Emit a ratio-spread intent. Optional: add a long $K_3 > K_1$ call to butterfly the tail. Do not route live orders. The optional wing is a different payoff once added.
7. **Hold.** Flatten on a grind through $S^\ast_{\mathrm{up}}$. Do not “wait for mean reversion” against unlimited calls. Waiting is how $L_{\max}$ is realized.

## 6. Execution protocol

- Only as a credit, or with a hard stop, because of unlimited upside. A credit is not a cap.
- Prefer converting to a call butterfly by buying a further OTM call. Until you do, this file’s $L_{\max}$ stands.
- Sell the extra $N_S - N_L$ calls only if inventory or a hedge already exists; this is a market-maker front-spread, not a retail income default.
- Size off the rally tail, not off $P_{\max}$. Sizing off peak profit is how the backtest lies.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **two call strikes**
- Contract multiplier for $N_L$, $N_S$
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events on the extra short calls

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $N_L:N_S$ | $1:2$ or $2:3$ | must have $N_L < N_S$ |
| $K_2$ | ITM | long calls |
| $K_1$ | near ATM | short calls, $K_1 > K_2$ |
| tenor | 1 week to 3 months | same expiry |
| $H$ | credit preferred | unlimited loss if wrong |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.ratio_call_spread` with:

1. `legs(spec) -> list[Leg]` — long $N_L$ calls $K_2$, short $N_S$ calls $K_1 > K_2$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_down` (if $H>0$), `S*_up`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1 > K_2$, $N_L < N_S$; refuse `n_long >= n_short`; $P_{\max}$ at $S_T=K_1$ matches the closed form.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unlimited rally.** This is the dangerous twin of the backspread. A buyout, squeeze, or trend week through $K_1$ is the path, not a slow fade you can roll.
- **Assignment** on extra short American calls, especially into a dividend. Extra short stock versus fewer long calls does not net to flat.
- **False income.** A credit is not a cap; $P_{\max}$ is the *best* case at $K_1$. Reporting only credit collected is how the backtest lies.
- **Front-running the ratio.** Legging the shorts first is an unhedged call sale.
- **Ratio mix-up.** $N_L>N_S$ is `069`. Do not share a payoff function without a count check.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $N_L(S_T-K_2)_+ - N_S(S_T-K_1)_+ - H$.
- At $S_T=K_1$, $f_T = P_{\max} = N_L(K_1-K_2)-H$.
- $f_T(S^\ast_{\mathrm{up}})=0$ within $10^{-8}$ relative to $S_0$; if $H>0$, also $f_T(S^\ast_{\mathrm{down}})=0$.
- Reject $N_L \ge N_S$ or $K_1 \le K_2$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
