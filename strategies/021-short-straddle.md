---
rank: 21
slug: short-straddle
title: "Short Straddle"
asset_class: "options"
style: "short volatility / income / undefined risk"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 021. Short Straddle

| Field | Value |
|---|---|
| Popularity rank (this kit) | 21 of 101 |
| Why it sits here | The textbook short-vol income trade. Widely used, widely blown up. Core of vol-selling programs. |
| Aliases | — |
| Asset class | options |
| Style | short volatility / income / undefined risk |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short ATM call and short ATM put. Net credit. Wins if the stock stays near $K$. Income strategy with unlimited loss.

You are betting that $\lvert S_T-K\rvert$ stays inside the credit $C$ you collected. Direction is not the bet: a rally and a crash of equal size lose the same at expiry. You are not running a defined-risk book. If the mandate forbids naked shorts, skip this file and use an iron butterfly. You are also not harvesting a typical P&L of $C$; that is the best case, attained only at a pin. The left and right tails fund every vol-risk-premium harvest that uses this shape.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the put is worth $K$ and $f_T=C-K$, a large loss. At $S_T=K$ both options die and $f_T=C=P_{\max}$. Far above $K$ the call is worth $S_T-K$ and $f_T=C-(S_T-K)$, unbounded negative.

## 2. First principles

A short European call with strike $K$ pays

$$
-(S_T - K)_+
$$

That is the right-hand hole. Below $K$ it is zero. Above $K$ it falls one-for-one without bound. Alone it is a naked short call. In the straddle it is half the absolute-move liability.

A short European put with the same strike pays

$$
-(K - S_T)_+
$$

That is the left-hand hole. Above $K$ it is zero. Below $K$ it falls one-for-one down to $-K$ if the stock goes to zero, which is still a large number. Same strike and same expiry are load-bearing.

Selling both brings in a credit $C$ at $t=0$. Adding the three pieces is the short straddle:

$$
f_T = -(S_T - K)_+ - (K - S_T)_+ + C
$$

$C$ is the sum of two bids (or better). It is not twice the mid. The package is short gamma and short vega at inception when $K\approx S_0$. Live marks can breach any comfort band long before expiry. This file's $f_T$ is the expiry identity only.

The two intrinsics sum to the absolute deviation from the strike, so

$$
f_T = C - |S_T - K|
$$

That is an inverted V centered at $K$. Profit is the credit minus the move. A large move either way is unbounded. You are not betting on direction. You are betting that $\lvert S_T-K\rvert$ stays inside the credit you collected.

That is the whole strategy. Everything below is how to pick $K$, how to refuse the trade when the mandate forbids naked shorts, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | common ATM strike |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$, quantity $1:1$, same $K$.

## 4. Mathematics

### 4.1 Terminal payoff

Short ATM call plus short ATM put, net credit $C$:

$$
f_T = -(S_T - K)_+ - (K - S_T)_+ + C = C - |S_T - K|
$$

The two writings are the same inverted V. Tests must match both. Sketch: $S_T=0$ prints $C-K$; $S_T=K$ prints $C$; $S_T\to\infty$ prints $-\infty$. There is no floor.

### 4.2 Break-evens

On the call side, $C-|S_T-K|=0$ with $S_T>K$:

$$
S^\ast_{\mathrm{up}} = K + C
$$

A rally of $C$ through the strike eats the credit. Beyond that every tick is a loss. For an ATM equity straddle, $C/S_0$ is often a few percent; that is not a wide safe zone.

On the put side, $C-|S_T-K|=0$ with $S_T<K$:

$$
S^\ast_{\mathrm{down}} = K - C
$$

A decline of $C$ through the strike eats the credit. If $K-C$ is close to zero, a crash still has room to run past the break-even by almost $K$. The profitable band $(K-C,\,K+C)$ is the whole trade.

### 4.3 Extrema

Maximum profit is the credit, attained at $S_T=K$:

$$
P_{\max} = C
$$

Pin is the designed outcome. Assignment friction, exercise, and a print a tick off $K$ all nibble this number. Treating $C$ as expected P&L is the usual blow-up: $C$ is the best case, not the mean.

Maximum loss is unbounded in either direction:

$$
L_{\max} = \text{unlimited}
$$

A gap either way is not capped. Margin will demand cash long before expiry on that path. Size off a stress $L$, never off $C$.

## 5. Step-by-step algorithm

1. **Universe.** Only if the mandate allows naked short options. Otherwise skip this file and use an iron butterfly or iron condor. This check exists because the shape is identical to those files' inner shorts without the wings. Skipping it is how defined-risk books become undefined.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ picks ATM $K$. A later print look-aheads the credit and the pin.
3. **Strike.** Choose $K$ ATM. A far-from-ATM pair is a short strangle. Document the listed strike, not a theoretical ATM.
4. **Expiry.** Short-dated weekly/monthly is the usual income tenor. Short-dated means more theta and more gamma into expiry. Longer-dated shorts collect more $C$ and live longer with unbounded tails.
5. **Size.** Sell $1$ ATM call and $1$ ATM put per lot. Size off a stress move, not off $C$. A 20% gap on a $\$100$ name is $\$20$ per share times $m$, minus $C$. That number, not the credit, is the lot count.
6. **Premium.** $C$ is the net credit actually received. Using mid inflates $P_{\max}$ and the apparent safe band.
7. **Blotter.** Emit a two-legged short-straddle intent. Do not route live orders. One ticket keeps you from selling one wing naked.
8. **Risk overlay.** Stop or delta-hedge if $\lvert S-K\rvert$ exceeds a fraction of $C$. That overlay is not part of expiry $f_T$. Without it, this file is hold-to-expiry with unlimited $L$.

## 6. Execution protocol

- Hard margin. Use defined-risk substitutes (iron butterfly, iron condor) unless the mandate allows naked shorts.
- Enter as a straddle (one ticket, net credit). Do not sell one wing without the other.
- Assignment and pin risk into expiry on both the call and the put.
- Cap lots by stress $L$ at a gap, not by credit harvested.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Margin parameters sufficient to refuse the ticket if naked shorts are not permitted
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K$ | ATM | listed strike nearest spot |
| tenor | weekly / monthly | income cluster |
| quantity | $1:1$ | short call and short put |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_straddle` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag. `L_max` is unbounded.
5. `validate(spec)` — same $K$ and expiry; qty $1:1$; both legs short; $P_{\max}=C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unlimited loss.** A gap either way is not capped. A 30% overnight move on a $\$100$ name is about $\$30$ per share against a credit of a few dollars, times $m$, times lots. That is how vol-sell books disappear.
- **Margin expansion.** The venue can demand more capital than $C$ long before expiry. A short straddle that is "making money on theta" can still be liquidated on a variation-margin call.
- **Pin.** $S_T=K$ is $P_{\max}$ only if both options expire without assignment friction. Pin through expiry can assign one side and leave you with a directional stock position into the next open.
- **This is the left tail** that funds vol-risk-premium harvests. Treating $C$ as a typical P&L is the usual blow-up. The mean of $C-|S_T-K|$ is not $C$.
- **One-legged fill.** Selling only the call (or only the put) is a naked directional short. The inverted-V identity is gone until the other wing is on.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $-(S_T-K)_+-(K-S_T)_++C$ and also $C-|S_T-K|$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K$, $f_T=C=P_{\max}$. As $\lvert S_T-K\rvert \to \infty$, $f_T \to -\infty$.
- Reject a spec with a long option leg, unequal strikes, or unequal quantities.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
