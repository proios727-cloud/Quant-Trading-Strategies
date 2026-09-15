---
rank: 43
slug: protective-call
title: "Protective Call"
asset_class: "options"
style: "hedge / bearish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 043. Protective Call

| Field | Value |
|---|---|
| Popularity rank (this kit) | 43 of 101 |
| Why it sits here | Standard insurance on a short stock book. Synthetic put. |
| Aliases | married call, synthetic put |
| Asset class | options |
| Style | hedge / bearish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short stock and long an ATM or OTM call with $K \ge S_0$. Hedges a squeeze.

You are betting that you want to stay short the name, and that a cap on the squeeze at $K$ is worth the insurance debit $D$. You are not running a standalone long-vol bet, and you are not buying a put as a crash lottery without the short. Without the short shares this file is a long call. You are also not buying a zero-loss guarantee: a squeeze through $K$ still leaves $L_{\max}=K-S_0+D$. Borrow is required; skip the name if it is missing.

Payoff sketch, one share, ignore financing: at $S_T=0$ the short is a total win minus $D$, so $f_T=S_0-D=P_{\max}$. At $S_T=K$ the call is at the money and $f_T=S_0-K-D=-L_{\max}$, the squeeze cap. Far above $K$ the call covers the short and $f_T$ stays at that cap.

## 2. First principles

A short share, marked from the sale price $S_0$, has terminal P&L

$$
S_0 - S_T
$$

That line is unbounded above as $S_T\to\infty$ (the squeeze) and bounded below by $S_0$ if the name goes to zero. The protective call exists because you want to keep the short's profit if the name falls, and replace the squeeze tail with a cap at $K$. The short identity does not change; the long call does.

A long European call with strike $K$ pays

$$
(S_T - K)_+
$$

The kink is at $K$. Below $K$ this piece is zero and the short is unhedged. Above $K$ it rises one-for-one, cancelling further squeeze loss. That cancellation is the insurance. An American call can be exercised early; the identity above is the European expiry claim.

Buying that call costs a debit $D$ at $t=0$. Adding the three pieces is the protective call:

$$
f_T = S_0 - S_T + (S_T - K)_+ - D
$$

$D$ shifts the whole payoff down by a constant and does not move the kink. Live P&L before expiry is not this identity. Borrow fees sit in financing, not in $f_T$. This file's $f_T$ is hold-to-expiry, European-style.

The call–put identity $(S_T-K)_+ - (K-S_T)_+ = S_T-K$ rewrites the same book as a long put plus cash:

$$
f_T = S_0 - K + (K - S_T)_+ - D
$$

That is why a married call is a synthetic put. The cash adjustment $S_0-K-D$ is the difference between short-stock-plus-call and owning the put outright. If you already short the shares, you overlay insurance. If you do not, buy the put instead of synthesizing it through borrow.

You are not running a standalone long-vol bet. You already short the shares; the call is the squeeze hedge. Downside (stock falling) is the short, reduced by $D$. Upside through $K$ is capped at $K-S_0+D$ of loss: the call covers the short above $K$.

That is the whole strategy. Everything below is how to locate borrow, how to pick $K$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying short-sale price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | long-call strike, $K \ge S_0$ |
| $D$ | call premium paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $Q$ | share count (negative = short) |
| $m$ | option multiplier (usually $100$) |

One long call covers $m$ short shares at hedge ratio $1.0$. Lot integrity is $\lvert Q\rvert = n m$ for integer $n \ge 1$.

## 4. Mathematics

### 4.1 Terminal payoff

Short stock plus long call, premium $D$ paid:

$$
f_T = S_0 - S_T + (S_T - K)_+ - D
= S_0 - K + (K - S_T)_+ - D
$$

The two lines are the same function of $S_T$. The first is the blotter. The second is the synthetic-put rewrite. Tests must match both. Sketch: $S_T=0$ prints $P_{\max}$; at $K$ and far above, $-L_{\max}$.

Above $K$ the call covers the short and $f_T = S_0 - K - D$. Below $K$ the call dies and $f_T = S_0 - S_T - D$.

### 4.2 Break-even

Set $f_T=0$ on the uncalled region $S_T < K$:

$$
S^\ast = S_0 - D
$$

The debit lowers the short's break-even: the name must fall $D$ just to get back to flat versus shorting unhedged at $S_0$. There is no second break-even above $K$: that region is the flat squeeze cap, usually a loss of $L_{\max}$.

### 4.3 Extrema

Maximum profit is the short going to zero, minus the debit:

$$
P_{\max} = S_0 - D
$$

A bankruptcy print still pays almost the short-sale proceeds, reduced by $D$. Hard-to-borrow fees can eat this number in financing even if $S_T\to 0$. That is outside $f_T$ and still real.

Maximum loss is the squeeze cap at $K$ plus the debit:

$$
L_{\max} = K - S_0 + D
$$

A squeeze through $K$ still loses the deductible $K-S_0$ plus the premium. ATM insurance ($K=S_0$) makes $L_{\max}=D$. Further OTM is cheaper and a worse cap. That tradeoff is the whole strike choice.

## 5. Step-by-step algorithm

1. **Universe.** Names you can short, with a liquid call chain. Price and ADV above a minimum. Keep delisted names until the delist date. Illiquid calls make $D$ untradeable. Survivorship would drop the names that squeezed, which is the event the hedge is for.
2. **Borrow.** Locate borrow first. If borrow is unavailable, skip the name. Do not put on the call as a standalone long. A long call without the short is a different file and a different $P_{\max}$.
3. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ is the short-sale mark and the moneyness of $K$. A later print look-aheads both.
4. **Strike.** Choose $K \ge S_0$. Default $K/S_0$ in $[1.00, 1.15]$. Higher $K$ is cheaper and a worse squeeze cap. A $K<S_0$ ITM call is a different overlay (more debit, less deductible).
5. **Size.** Short $\lvert Q\rvert$ shares, $\lvert Q\rvert$ a multiple of $m$. Buy $\lvert Q\rvert/m$ calls. Extra calls are a long-vol add-on. Fewer calls leave a hole in $L_{\max}$.
6. **Premium.** $D$ is the debit actually paid. $D$ is not the mid. Using mid understates $L_{\max}$ and $S^\ast$.
7. **Blotter.** Emit intents: short stock, long call. Do not route live orders. Refuse the ticket if borrow is missing.
8. **Hold / roll.** Hold to expiry. Roll the call if the short remains and insurance is still required. Rolling is a new $D$. A recall unwinds the short whether or not the call is still on; do not keep the call and skip the short.

## 6. Execution protocol

- Locate borrow first. Buy the call as the squeeze hedge, not as a standalone long-vol bet.
- Default fill: next available after borrow is confirmed and the chain is known.
- Borrow fees and rebate enter financing, not $f_T$. A recall unwinds the short whether or not the call is still on.
- Cap $\lvert Q\rvert$ by ADV and by borrow depth.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- **Borrow availability and fees** for the short stock leg
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, any buy-in or recall of the short, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: book value, earnings.

No restatement peeking. Delisted names stay in the sample until the delist date. If borrow disappears, drop the name; do not keep the long call and skip the short.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K/S_0$ | $[1.00, 1.15]$ | ATM to 15% OTM call |
| hedge ratio | $1.0$ | $1$ call per $m$ short shares |
| $m$ | $100$ | US equity listed default |
| borrow | required | skip if unavailable |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.protective_call` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K \ge S_0$; $\lvert Q\rvert$ a multiple of $m$; call qty $=\lvert Q\rvert/m$; stock side short; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing. Refuse the ticket if borrow is missing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Borrow recall.** The short can be bought in; the call then becomes a naked long. A buy-in at a squeezed print realizes the stock loss and leaves you long a call you bought as insurance, not as a directional bet.
- **Debit drag.** $D$ compounds if you roll every month. Twelve 1% ATM calls on an unchanged short cost about 12% a year before the cap ever pays.
- **Squeeze through $K$.** The cap is $L_{\max}=K-S_0+D$, not zero. A 20% squeeze against a 10% OTM call still loses the 10% deductible plus $D$.
- **Hard-to-borrow fees.** Financing can erase $P_{\max}$ even if $S_T\to 0$. A 30% annual borrow fee on a three-month hold is not in $f_T$ and can still dominate the short's intended profit.
- **Partial hedge.** Buying fewer than $\lvert Q\rvert/m$ calls because "the call is rich" leaves a hole. The unhedged residual is the original squeeze on that fraction.

## 11. Acceptance tests

- Two-piece identity: on a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $S_0-S_T+(S_T-K)_+-D$ and also $S_0-K+(K-S_T)_+-D$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=0$, $f_T=S_0-D=P_{\max}$. For $S_T\ge K$, $f_T=S_0-K-D=-L_{\max}$.
- Synthetic-put: the protective-call $f_T$ matches a long put with the same $K$ and a cash adjustment $S_0-K-D$.
- Reject a spec with no borrow flag, $K<S_0$ when the mandate is ATM-or-OTM, or call qty exceeding $\lvert Q\rvert/m$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
