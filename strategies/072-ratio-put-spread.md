---
rank: 72
slug: ratio-put-spread
title: "Ratio Put Spread"
asset_class: "options"
style: "neutral to bullish / income if credit"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 072. Ratio Put Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 72 of 101 |
| Why it sits here | Front-spread on puts. Income if credit; crash risk is large but finite. |
| Aliases | put front-spread |
| Asset class | options |
| Style | neutral to bullish / income if credit |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short $N_S$ near-ATM puts $K_1$ and long $N_L < N_S$ ITM puts $K_2 > K_1$. Typical ratios $1\times 2$ or $2\times 3$. Opposite of the put ratio backspread: peak between the strikes, large defined loss at $S_T = 0$.

You are betting that spot stays above $S^\ast_{\mathrm{down}}$, ideally pinning near $K_1$. You are selling crash convexity. You are not running a defined-risk put credit spread with matched counts: extra shorts make the loss at zero large. Unlike `071`, loss is finite (stock cannot go below zero), but $L_{\max}$ can still be a large fraction of notional.

The typical user wants put-side income or a market-maker front-spread. Horizon is one expiry. Size off $L_{\max}$ at zero, not off credit. Refuse $N_L \ge N_S$. Flatten if spot tests $S^\ast_{\mathrm{down}}$. Do not average extra short puts into a crash. A further OTM long put toward a butterfly cuts $L_{\max}$; until it is on, this file’s crash identity stands.

## 2. First principles

Two listed put strikes, same expiry, **more shorts than longs**. The long ITM package pays $N_L(K_2-S_T)_+$. The short near-ATM package pays $-N_S(K_1-S_T)_+$. Subtract net premium paid $H$:

$$
f_T = N_L (K_2 - S_T)_+ - N_S (K_1 - S_T)_+ - H
$$

Same algebraic family as `070`; $N_S>N_L$ flips it. Extra shorts dominate as $S_T\to 0$. $H$ shifts the map. Refuse `n_long >= n_short` so this cannot silently become a backspread.

Above $K_2$ both puts expire worthless, so $f_T = -H$. A debit ($H>0$) needs a pullback through an upper break-even.

Between $K_1$ and $K_2$ only the longs are in the money. P&L peaks at $S_T = K_1$:

$$
P_{\max} = N_L(K_2 - K_1) - H
$$

Best case, not a floor. Each long put is in by the strike gap; the extra shorts at $K_1$ have not started to pay. If this number is not positive, reject. Pin at $K_1$ is also where the extra shorts begin to bite if spot ticks through.

Below $K_1$ the extra short puts take over. At $S_T = 0$ every put is worth its strike, and the extra shorts dominate:

$$
L_{\max} = N_S K_1 - N_L K_2 + H
$$

That is the crash print. Finite, often large. Credit ($H<0$) reduces it; debit adds. Size off this, always. Assignment can realize a similar hole before expiry via share delivery that the $N_L$ longs do not offset one-for-one.

That is the whole strategy. You are selling crash convexity. Crash to zero realizes $L_{\max}$. Size off that, not off credit.

**Payoff sketch.** Long 1 ITM at $K_2$, short 2 ATM at $K_1<K_2$. At $S_T=0$, $f_T=-L_{\max}$ (crash hole). At $S_T=K_1$, peak $P_{\max}$. Far above $K_2$, both puts die: $f_T=-H$ (keep a credit). The sketch is a tent with a deep but finite left wall.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2$ | short near-ATM put strike, long ITM put strike |
| $N_L$ | number of long $K_2$ puts |
| $N_S$ | number of short $K_1$ puts, $N_S > N_L$ |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry |

Default example: long 1 ITM put $K_2$, short 2 ATM puts $K_1 < K_2$. Refuse $N_L \ge N_S$.

## 4. Mathematics

### 4.1 Premium

Income if credit ($H<0$). A debit still has a peak at $K_1$ but starts from a hole and still bears the crash $L_{\max}$. Prefer $H<0$ only after $L_{\max}$ clears a caller cap. Credit is not a bound on the crash.

### 4.2 Terminal payoff

$$
f_T = N_L (K_2 - S_T)_+ - N_S (K_1 - S_T)_+ - H
$$

Implement this exactly. Grid tests must hit $-L_{\max}$ at $0$ and $P_{\max}$ at $K_1$. Strike order $K_2>K_1$ is required so the long is the ITM put.

### 4.3 Break-evens

When $H>0$, an upper break-even sits below $K_2$:

$$
S^\ast_{\mathrm{up}} = K_2 - \frac{H}{N_L} \qquad (H>0)
$$

A debit needs the longs to earn $H$ on a pullback. Omit this key when $H\le 0$: above $K_2$ a credit is already profit. Do not reuse the formula on a credit structure.

The lower break-even, below $K_1$, is where the extra shorts have given back the peak:

$$
S^\ast_{\mathrm{down}} = \frac{N_S K_1 - N_L K_2 + H}{N_S - N_L}
$$

Below this print the crash hole is open. Flatten if spot tests it. A debit moves $S^\ast_{\mathrm{down}}$ up (less room). This is the analogue of $S^\ast_{\mathrm{up}}$ in `071`.

### 4.4 Max profit and loss

Peak at $S_T = K_1$:

$$
P_{\max} = N_L(K_2 - K_1) - H
$$

At $S_T = 0$:

$$
L_{\max} = N_S K_1 - N_L K_2 + H
$$

Unlike the call front-spread, loss is defined. It can still be a large fraction of notional. Tests should check both closed forms. If $L_{\max}$ is small relative to $P_{\max}$, check the ratio: extra shorts should make the crash hole deep.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. Assignment cascades on short American puts can realize $L_{\max}$ before expiry. Carry $\Delta, \Gamma, \Theta, \nu$ if you hedge; hedging does not remove the extra short-put tail to zero. A delta-hedged front-spread can still gap to a large long-stock book from the shorts.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed puts at two strikes, same expiry. The short $K_1$ line must absorb $N_S$ contracts, and borrow/assignment mechanics must be acceptable. Extra shorts are the crash risk; if assignment into stock is not acceptable, skip.
2. **Strikes and ratio.** $K_2$ ITM, $K_1$ near ATM, $K_2 > K_1$. Set $N_L:N_S = 1:2$ or $2:3$. Refuse $N_L \ge N_S$. That refuse is the front-spread gate.
3. **Legs.** Buy $N_L$ puts $K_2$, sell $N_S$ puts $K_1$. Longs first if you must leg.
4. **Premium.** Compute $H$ and $L_{\max} = N_S K_1 - N_L K_2 + H$. Reject if $L_{\max}$ exceeds a caller cap. Prefer $H<0$ only after that check. The order is load-bearing: credit after crash cap, not instead of it.
5. **Metrics.** Store $S^\ast_{\mathrm{up}}$ (if $H>0$), $S^\ast_{\mathrm{down}}$, $P_{\max}$, $L_{\max}$. $L_{\max}$ is finite; do not store unlimited.
6. **Blotter.** Emit a ratio-put intent. Do not route live orders.
7. **Hold.** Flatten if spot tests $S^\ast_{\mathrm{down}}$. Do not average extra short puts into a crash. Averaging is how $L_{\max}$ is exceeded intra-day before expiry even prints it.

## 6. Execution protocol

- Crash to zero realizes $L_{\max}$. Size off that, not off credit. A $1\times 2$ that “only” collected a small credit can still lose $K_1$ extra per extra short.
- Enter longs first if you must leg. Extra short puts without the ITM long are a naked-ratio disaster.
- Assignment on the $N_S$ shorts can create a long-stock book; the $N_L$ longs do not offset share-for-share. Plan locate/borrow as if you might be long the extra shares.
- A further OTM long put converts this toward a put butterfly and cuts $L_{\max}$. Until that wing is on, do not report butterfly risk.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **two put strikes**
- Contract multiplier for $N_L$, $N_S$
- Borrow/assignment mechanics if shorts can be exercised into stock
- Dividends and rates if you mark to a model
- At expiry: settlement print and American early-exercise events

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $N_L:N_S$ | $1:2$ or $2:3$ | must have $N_L < N_S$ |
| $K_2$ | ITM | long puts |
| $K_1$ | near ATM | short puts, $K_1 < K_2$ |
| tenor | 1 week to 3 months | same expiry |
| $L_{\max}$ cap | caller-set | size off crash P&L |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.ratio_put_spread` with:

1. `legs(spec) -> list[Leg]` — long $N_L$ puts $K_2$, short $N_S$ puts $K_1 < K_2$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written above.
4. `metrics(spec) -> dict` — `S*_up` (if $H>0$), `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_2 > K_1$, $N_L < N_S$; $P_{\max}$ at $S_T=K_1$ and $L_{\max}$ at $S_T=0$ match the closed forms.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Crash to zero.** Large defined loss $L_{\max}$. A gap on a profit warning or a bank-name weekend is the path; you do not need unlimited loss for the book to be unusable.
- **Assignment cascade** on short puts, share delivery not offset 1:1 by the longs. Overnight you can be long extra shares versus remaining puts.
- **False income.** Credit is not a bound on $L_{\max}$. Reporting only premium collected is how the backtest lies.
- **Pin at $K_1$.** Peak profit is also where the extra shorts start to bite. Settlement at the short strike is operationally messy.
- **Ratio mix-up.** $N_L>N_S$ is `070` and *profits* at zero. Validate counts.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $N_L(K_2-S_T)_+ - N_S(K_1-S_T)_+ - H$.
- At $S_T=0$, $f_T = -L_{\max} = -N_S K_1 + N_L K_2 - H$.
- At $S_T=K_1$, $f_T = P_{\max} = N_L(K_2-K_1)-H$.
- Reject $N_L \ge N_S$ or $K_2 \le K_1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves break-evens only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
