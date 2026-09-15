---
rank: 44
slug: covered-put
title: "Covered Put"
asset_class: "options"
style: "income / mildly bearish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 044. Covered Put

| Field | Value |
|---|---|
| Popularity rank (this kit) | 44 of 101 |
| Why it sits here | Symmetric to the covered call, used on short stock books. Same payoff as a short call. |
| Aliases | sell-write |
| Asset class | options |
| Style | income / mildly bearish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short stock and short a put with strike $K$. Income by selling OTM puts against the short. Unlimited loss if the stock rallies.

You are betting that the stock stays above $K$ through expiry, or that a modest decline is worth more than the extra $C$ only up to $K$. Assignment on the put *covers* the short (you buy the stock at $K$). You are not running a defined-risk short: a rally is the short stock with no call hedge, unbounded. You are not running a covered call; the symmetry is payoff-shape, not a cap in both directions. Borrow is required.

Payoff sketch, one share, ignore financing: at $S_T=0$ the put is assigned and $f_T=S_0-K+C=P_{\max}$. At $S_T=K$ the put is at the money and you are still at $P_{\max}$. Far above $K$ the put dies and $f_T=S_0-S_T+C$, unbounded negative.

## 2. First principles

A short share, marked from the sale price $S_0$, has terminal P&L

$$
S_0 - S_T
$$

Unbounded as $S_T\to\infty$. The covered put exists because you are willing to sell some of the short's extra profit below $K$ in exchange for cash today. The short identity does not change; the short put does.

A short European put with strike $K$ pays

$$
-(K - S_T)_+
$$

The kink is at $K$. Above $K$ the put dies and this piece is zero. Below $K$ it falls one-for-one as $S_T$ falls, cancelling the short's further gain. That cancellation is the designed cap on the *downside* of the short, not on the rally. Assignment buys the stock at $K$ and covers the short.

Selling that put brings in a credit $C$ at $t=0$. Adding the three pieces is the covered put:

$$
f_T = S_0 - S_T - (K - S_T)_+ + C
$$

$C$ shifts the whole payoff up by a constant and does not move the kink. Live P&L before expiry is not this identity. Borrow fees sit in financing. This file's $f_T$ is hold-to-expiry, European-style.

The call–put identity rewrites the same book as a short call plus cash:

$$
f_T = S_0 - K - (S_T - K)_+ + C
$$

That is why a covered put is not a new shape. It is a short call financed with a short-stock-plus-bond package. A rally is not covered: both the short stock and the expired put lose as $S_T$ rises. This is not a defined-risk short.

You already short the shares. Selling the put is income against that short, and assignment on the put *covers* the short (you buy the stock at $K$). A rally is not covered: both the short stock and the expired put lose as $S_T$ rises. This is not a defined-risk short.

That is the whole strategy. Everything below is how to locate borrow, how to pick $K$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying short-sale price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | short-put strike, typically $K \le S_0$ |
| $C$ | put premium received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $Q$ | share count (negative = short) |
| $m$ | option multiplier (usually $100$) |

One short put covers $m$ short shares. Lot integrity is $\lvert Q\rvert = n m$ for integer $n \ge 1$.

## 4. Mathematics

### 4.1 Terminal payoff

Short stock plus short put, premium $C$ received:

$$
f_T = S_0 - S_T - (K - S_T)_+ + C
= S_0 - K - (S_T - K)_+ + C
$$

The two lines are the same function of $S_T$. The first is the blotter. The second is the short-call rewrite. Tests must match both. Sketch: $S_T=0$ prints $P_{\max}$; at $K$ still $P_{\max}$; far above, $-\infty$.

Below $K$ the put is assigned and $f_T = S_0 - K + C$. At or above $K$ the put dies and $f_T = S_0 - S_T + C$.

### 4.2 Break-even

Set $f_T=0$ on the unput region $S_T > K$:

$$
S^\ast = S_0 + C
$$

The credit raises the short's break-even: the name can rally $C$ before the overlay is worse than shorting unhedged at $S_0$. There is no second break-even below $K$: that region is the flat cap at $P_{\max}$.

### 4.3 Extrema

Maximum profit is the short down to $K$ plus the credit:

$$
P_{\max} = S_0 - K + C
$$

A collapse through $K$ does not pay more. Assignment covers the short at $K$. Choosing $K$ further OTM (lower) buys back some extra short profit by giving up some $C$.

Maximum loss is unbounded as $S_T \to \infty$:

$$
L_{\max} = \text{unlimited}
$$

A rally is the short stock with no call hedge. Do not book this as a covered-call analogue with a cap in both directions. Size off a rally stress, not off $C$.

## 5. Step-by-step algorithm

1. **Universe.** Names you can short, with a liquid put chain. Price and ADV above a minimum. Keep delisted names until the delist date. Illiquid puts make $C$ untradeable. Survivorship would drop names that squeezed, which is $L_{\max}$.
2. **Borrow.** Locate borrow first. If borrow is unavailable, skip the name. A short put without the short stock is a naked short put, not this file.
3. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ is the short-sale mark and the moneyness of $K$. A later print look-aheads both.
4. **Strike.** Sell put $K \le S_0$ (OTM from the short’s perspective). Default 2–10% below spot. Lower $K$ collects less $C$ and keeps more of the short's decline. ATM maximizes income and minimizes $P_{\max}$.
5. **Expiry.** Monthly tenor unless the mandate says otherwise. Weeklies are more roll cost. A LEAP short put against a short stock is a long-dated naked-ish package this file does not default to.
6. **Size.** Short $\lvert Q\rvert$ shares, $\lvert Q\rvert$ a multiple of $m$. Sell $\lvert Q\rvert/m$ puts. Do not oversell puts against the short. Extra short puts are naked. Lot integrity keeps assignment a round cover.
7. **Premium.** $C$ is the credit actually received. $C$ is not the mid. Using mid inflates $P_{\max}$ and the apparent rally cushion $S^\ast$.
8. **Blotter.** Emit intents: short stock, short put. Do not route live orders. If assigned, the short put covers the short stock (you buy the stock at $K$). Refuse the ticket if borrow is missing.

## 6. Execution protocol

- Requires borrow. Prefer selling the put as a limit at the bid or better.
- Assignment on the short put covers the short stock (you buy the stock at $K$). That is the designed cap on the *downside* of the short, not on the rally.
- Cap $\lvert Q\rvert$ by ADV and by borrow depth. Size off a rally stress, not off $C$.
- Hard-to-borrow fees enter financing, not $f_T$.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- **Borrow availability and fees** for the short stock leg
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, any buy-in or recall of the short, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: book value, earnings.

No restatement peeking. Delisted names stay in the sample until the delist date. If borrow disappears, drop the name; do not keep the short put and skip the short stock.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K/S_0$ | $0.90$–$0.98$ | OTM put 2–10% below spot |
| tenor | monthly | income cluster |
| $Q$ | multiple of $m$, short | one short put per $m$ shares |
| $m$ | $100$ | US equity listed default |
| borrow | required | skip if unavailable |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.covered_put` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag. `L_max` is unbounded.
5. `validate(spec)` — $\lvert Q\rvert$ a multiple of $m$; one short put per $m$ short shares; stock side short; $P_{\max}=S_0-K+C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing. Refuse the ticket if borrow is missing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unlimited upside.** A rally is the short stock with no call hedge. A 40% squeeze on a $\$50$ name is $\$20$ per share against a put credit of a dollar or two, times $m$. That is not a covered-call analogue.
- **Hard-to-borrow.** Recall turns the short put into a naked short put. You lose the cover (the short stock is bought in) and keep the short put, which is the opposite of the designed assignment cover.
- **Not defined-risk.** Do not book this as a covered-call analogue with a cap in both directions. The covered call caps the right tail of a long. This file caps the left tail of a short and leaves the right tail open.
- **Assignment timing.** Early put assignment covers the short before you chose to cover. You can be flat the stock, still short a put that is now naked if you sold more than one, or simply out of a short you wanted to keep.
- **Credit-sizing.** Sizing off $C$ rather than a rally stress is the usual blow-up. The income looks small and steady until the squeeze.

## 11. Acceptance tests

- Two-piece identity: on a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $S_0-S_T-(K-S_T)_++C$ and also $S_0-K-(S_T-K)_++C$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K$ (and below), $f_T=S_0-K+C=P_{\max}$. As $S_T\to\infty$, $f_T\to-\infty$.
- Put-call: the covered-put $f_T$ matches a short call with the same $K$ and $C$ plus a cash bond of $S_0-K$.
- Reject a spec with no borrow flag, $\lvert Q\rvert$ not a multiple of $m$, or more short puts than $\lvert Q\rvert/m$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
