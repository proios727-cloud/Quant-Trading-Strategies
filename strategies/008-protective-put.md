---
rank: 8
slug: protective-put
title: "Protective Put"
asset_class: "options"
style: "hedge / bullish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 008. Protective Put

| Field | Value |
|---|---|
| Popularity rank (this kit) | 8 of 101 |
| Why it sits here | Standard portfolio-insurance overlay. Married-put and synthetic-call language is universal in listed-option desks. |
| Aliases | married put, synthetic call |
| Asset class | options |
| Style | hedge / bullish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long stock and long an ATM or OTM put with $K \le S_0$. Caps the left tail; unlimited upside after paying debit $D$. Same payoff as a long call (synthetic call).

You are betting that you want to stay long the name, and that a floor at $K$ is worth the insurance debit. You are not fading the stock, and you are not buying a put as a standalone crash lottery. Without the shares this file is a long put, which has a different $P_{\max}$ and a different reason to exist. You are also not buying a zero-loss guarantee: a gap through $K$ still leaves $L_{\max}=S_0-K+D$.

Payoff sketch, one share, ignore financing: at $S_T=0$ the put pays $K$ and $f_T=K-S_0-D=-L_{\max}$. At $S_T=K$ the put is at the money and $f_T=K-S_0-D$, still the floor. Far above $K$ the put dies and $f_T=S_T-S_0-D$, the stock reduced by the premium you paid.

## 2. First principles

A long share, marked from the purchase price $S_0$, has terminal P&L

$$
S_T - S_0
$$

That line is the unhedged book. It goes to $-S_0$ if the name goes to zero. The protective put exists because you want to keep the slope of $+1$ above $K$ and replace the left tail with a floor. The stock identity does not change; the long put does.

A long European put with strike $K$ pays the intrinsic

$$
(K - S_T)_+
$$

The kink is at $K$. Above $K$ this piece is zero. Below $K$ it rises one-for-one as $S_T$ falls, cancelling the stock's further loss. That cancellation is the insurance. An American put can be exercised early; the identity above is the European expiry claim.

Buying that put costs a debit $D$ at $t=0$. Adding the three pieces is the protective put:

$$
f_T = S_T - S_0 + (K - S_T)_+ - D
$$

$D$ is cash you already spent. It shifts the whole payoff down by a constant and does not move the kink. Live P&L before expiry is not this identity: implied vol and rates sit in the mark. This file's $f_T$ is hold-to-expiry, European-style.

The call–put identity $(S_T-K)_+ - (K-S_T)_+ = S_T-K$ rewrites the same book as a long call plus cash:

$$
f_T = K - S_0 + (S_T - K)_+ - D
$$

That is why a married put is a synthetic call. The cash adjustment $K-S_0-D$ is the difference between owning stock-plus-put and owning the call outright. If you already own the shares, you overlay insurance. If you do not, buy the call instead of synthesizing it the expensive way.

You are not fading the stock. You are buying a floor at $K$ so a gap-down cannot take more than $S_0-K+D$. Upside above $K$ is the stock, reduced by the insurance debit.

That is the whole strategy. Everything below is just how to pick $K$, how to size the hedge ratio, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying purchase price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | long-put strike, $K \le S_0$ |
| $D$ | put premium paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $Q$ | share count (positive = long) |
| $m$ | option multiplier (usually $100$) |

One long put covers $m$ shares at hedge ratio $1.0$. Lot integrity is $Q = n m$ for integer $n \ge 1$ unless the hedge ratio is deliberately smaller.

## 4. Mathematics

### 4.1 Terminal payoff

Stock plus long put, premium $D$ paid:

$$
f_T = S_T - S_0 + (K - S_T)_+ - D
= K - S_0 + (S_T - K)_+ - D
$$

The two lines are the same function of $S_T$. The first is the blotter (stock, long put, debit). The second is the synthetic-call rewrite. Tests must match both on a dense grid.

Below $K$ the put is in the money and $f_T = K - S_0 - D$. At or above $K$ the put dies and $f_T = S_T - S_0 - D$. Sketch: $S_T=0$ prints $-L_{\max}$; $S_T=K$ is still the floor; $S_T\to\infty$ rises one-for-one, unlimited.

### 4.2 Break-even

Set $f_T=0$ on the unput region $S_T > K$:

$$
S^\ast = S_0 + D
$$

The debit raises the stock's break-even by $D$. That is the cost of the floor: the name must rally $D$ just to get back to flat versus buying unhedged at $S_0$. There is no second break-even below $K$: that region is the flat floor, usually a loss of $L_{\max}$.

### 4.3 Extrema

Maximum profit is unbounded as $S_T \to \infty$:

$$
P_{\max} = \text{unlimited}
$$

The put does not cap the right tail. Once $S_T>K$, you own the stock reduced by $D$. A protective-put book that "lags in a bull market" is the debit, not a tracking-error mystery.

Maximum loss is the floor at $K$ plus the debit:

$$
L_{\max} = S_0 - K + D
$$

A gap through $K$ still loses the deductible $S_0-K$ plus the premium. ATM insurance ($K=S_0$) makes $L_{\max}=D$. Deep OTM insurance is cheaper and leaves a larger deductible. That tradeoff is the whole strike choice.

## 5. Step-by-step algorithm

1. **Universe.** Listed names you already hold or will buy, with a liquid put chain. Price and ADV above a minimum. Keep delisted names until the delist date (no survivorship). Illiquid puts make $D$ untradeable. Survivorship would drop the names that hit the floor, which is the event the hedge is for.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ is the purchase mark in $f_T$ and the moneyness of $K$. A later print look-aheads both.
3. **Strike.** Choose $K \le S_0$. Default $K/S_0$ in $[0.85, 1.00]$: 5–15% OTM for a collar-like hedge, ATM for tight insurance. Lower $K$ is cheaper and a worse floor. A $K>S_0$ ITM put is a different overlay (more debit, less deductible) and is not this file's default mandate.
4. **Expiry.** Tenor 1–6 months unless the insurance window is shorter. Insurance that expires before the event is not insurance. A LEAP costs more $D$ and decays slower; a weekly is a rolling tax if you rebuy every Friday.
5. **Size.** Hold or buy $Q$ shares. Buy $Q/m$ puts at hedge ratio $1.0$, or fewer puts if you want residual downside. Extra puts are a crash lottery on top of the stock, not this overlay. Fewer puts leave a hole in $L_{\max}$.
6. **Premium.** $D$ is the debit actually paid (ask or better on the long). $D$ is not the mid. Using mid understates $L_{\max}$ and the break-even $S^\ast$.
7. **Blotter.** Emit intents: long stock, long put. Do not route live orders. The spec stops at intent.
8. **Hold / roll.** Hold to expiry. Roll before expiry if insurance is still required. If $S_T \gg K$, the put expires worthless and $D$ is the insurance premium. Rolling is a new trade with a new $D$; compounding that debit is how overlay insurance eats a bull market.

## 6. Execution protocol

- Default fill: next available auction or limit after $S_0$ and the chain are known.
- Buy the put on the offer only if the hedge is urgent; otherwise work a limit between mid and ask.
- Cap $Q$ by ADV. A hedge that cannot be lifted is not a hedge.
- If you already hold the stock, do not re-buy it; overlay the put on the existing long.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: borrow (the stock leg is long), book value, earnings.

No restatement peeking. Delisted names stay in the sample until the delist date.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K/S_0$ | $[0.85, 1.00]$ | 5–15% OTM vs ATM insurance |
| tenor | 1–6 months | match the insurance window |
| hedge ratio | $1.0$ | $1$ put per $m$ shares |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.protective_put` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K \le S_0$; $Q$ a multiple of $m$ at hedge ratio $1.0$; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Debit drag.** $D$ compounds if you roll every month. Twelve 1% ATM puts on an unchanged name cost about 12% a year before the floor ever pays. That is a concrete tax, not a rounding error.
- **Skew.** OTM puts are expensive when the put wing is bid. A 10% OTM put in a crash-scared index can cost as much as an ATM put did the month before; $L_{\max}$ barely shrinks and $S^\ast$ moves a long way up.
- **Floor, not zero.** A gap through $K$ still leaves $L_{\max} = S_0-K+D$. Overnight halving of a name with a 15% OTM put still loses the 15% deductible plus $D$.
- **Wrong tenor.** Insurance that expires before the event is not insurance. A put that dies on Thursday does not cover Friday's print.
- **Partial hedge.** Buying fewer than $Q/m$ puts because "vol is rich" leaves a hole. The unhedged residual is the original stock left tail on that fraction.

## 11. Acceptance tests

- Two-piece identity: on a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $S_T-S_0+(K-S_T)_+-D$ and also $K-S_0+(S_T-K)_+-D$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=0$, $f_T=-L_{\max}$. For $S_T>K$, $f_T$ rises one-for-one with $S_T$.
- Synthetic-call: the protective-put $f_T$ matches a long call with the same $K$ and a cash adjustment $K-S_0-D$.
- Reject a spec with $K > S_0$ when the mandate is OTM-or-ATM insurance, or with put qty exceeding $Q/m$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
