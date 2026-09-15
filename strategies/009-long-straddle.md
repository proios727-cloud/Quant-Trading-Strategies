---
rank: 9
slug: long-straddle
title: "Long Straddle"
asset_class: "options"
style: "long volatility / non-directional"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 009. Long Straddle

| Field | Value |
|---|---|
| Popularity rank (this kit) | 9 of 101 |
| Why it sits here | The canonical long-vol package. Every vol desk and every event-vol trade starts here. |
| Aliases | — |
| Asset class | options |
| Style | long volatility / non-directional |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long ATM call and long ATM put, same $K$. Net debit. Wins on a large move either way. Capital-gain volatility trade.

You are betting that $\lvert S_T-K\rvert$ exceeds the premium $D$ you paid. Direction is not the bet: a rally and a crash of equal size pay the same at expiry. You are not selling vol, and you are not running a delta-hedged variance book unless you add a hedge this file does not include. Sitting still loses $D$. Implied-vol crush after a known event can mark the package worse than expiry $L_{\max}$ if you exit early.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the put is worth $K$ and $f_T=K-D$, which is a profit if $K>D$ (it is). At $S_T=K$ both options die and $f_T=-D=-L_{\max}$. Far above $K$ the call is worth $S_T-K$ and $f_T=S_T-K-D$, unbounded.

## 2. First principles

A long European call with strike $K$ pays

$$
(S_T - K)_+
$$

That is the right-hand wing. It is zero below $K$ and then rises one-for-one. Alone it is a bullish debit. In the straddle it is half the absolute-move claim.

A long European put with the same strike pays

$$
(K - S_T)_+
$$

That is the left-hand wing. It is zero above $K$ and then rises one-for-one as $S_T$ falls. Alone it is a bearish debit. Same strike and same expiry are load-bearing: different strikes make a strangle; different expiries make a time spread.

Buying both costs a debit $D$ at $t=0$. Adding the three pieces is the long straddle:

$$
f_T = (S_T - K)_+ + (K - S_T)_+ - D
$$

$D$ is the sum of two asks (or better). It is not twice the mid. The package is long gamma and long vega at inception when $K\approx S_0$; those Greeks are why the live mark moves before expiry. This file's $f_T$ ignores them.

Exactly one of the two intrinsics is nonzero (except at $S_T=K$, where both are zero), so the sum is the absolute deviation from the strike:

$$
f_T = \lvert S_T - K\rvert - D
$$

That is the whole shape: a V centered at $K$, shifted down by $D$. Profit begins only after the move has paid for both premiums. You are not betting on direction. You are betting that $\lvert S_T-K\rvert$ exceeds the premium you paid. Sitting still loses $D$.

That is the whole strategy. Everything below is just how to pick $K$ and tenor, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | common ATM strike, $K \approx S_0$ |
| $D$ | net debit paid at $t=0$ (call premium plus put premium) |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs are the same expiry $T$, same underlying, quantity $1:1$.

## 4. Mathematics

### 4.1 Terminal payoff

Long ATM call plus long ATM put, net debit $D$:

$$
f_T = (S_T - K)_+ + (K - S_T)_+ - D = |S_T - K| - D
$$

The two writings are the same V. Tests must match both. Sketch: $S_T=0$ prints $K-D$; $S_T=K$ prints $-D$; $S_T\to\infty$ prints $S_T-K-D$. There is no interior plateau; every tick away from $K$ at expiry helps.

### 4.2 Break-evens

On the call side, $|S_T-K|-D=0$ with $S_T>K$:

$$
S^\ast_{\mathrm{up}} = K + D
$$

The name must finish at least $D$ above the strike. For an ATM straddle that is roughly a $D/S_0$ relative move, before costs. Implied vol already priced a typical move of that order; you need more than typical, or you need to exit on a vol expansion before expiry.

On the put side, $|S_T-K|-D=0$ with $S_T<K$:

$$
S^\ast_{\mathrm{down}} = K - D
$$

Same distance the other way. If $K-D\le 0$, the down-side break-even is at or below zero and a total wipe-out of the stock still profits by $K-D$. That is rare on a short-dated ATM equity straddle and common only when $D$ is a large fraction of $K$.

### 4.3 Extrema

Maximum profit is unbounded in either direction:

$$
P_{\max} = \text{unlimited}
$$

A takeover print or a bankruptcy print both pay. The straddle does not care which. In practice you often exit into the event; expiry $P_{\max}$ is then a bound, not a realized number.

Maximum loss is the debit, attained at $S_T=K$:

$$
L_{\max} = D
$$

Pin risk is the expiry story: the name closes on the strike and both options expire worthless. Before expiry, an implied-vol crush can mark the package for more than $D$ of pain if you liquidate; $L_{\max}=D$ is an expiry identity, not a live stop.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with a tight ATM straddle. Open interest and bid–ask on both wings above a minimum. A wide two-sided spread makes $D$ a guess. Indexes are usually cleaner than single names into events.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ picks the listed strike nearest ATM. A later print can flip which strike is ATM and look-ahead the debit.
3. **Strike.** Choose $K \approx S_0$, the listed strike nearest the spot (or the delta-neutral pair if the mandate is delta-1 vol). A far-from-ATM pair is a strangle. Delta-neutral may split the strike by a tick; document it.
4. **Expiry.** Tenor 7–45 days for event vol; longer only for vol-of-vol. The event must sit inside the life of both options. A straddle that expires the morning of earnings is not an earnings trade.
5. **Size.** Buy $1$ ATM call and $1$ ATM put per lot. Scale lots by ADV and margin; do not leg into a naked call. One-legged fills turn a vol bet into a directional long option. That is a different file.
6. **Premium.** $D$ is the sum of debits actually paid. $D$ is not twice the mid. Record each fill. Tests compare $f_T$ to this $D$, not to a model value.
7. **Blotter.** Emit a two-legged straddle intent. Do not route live orders. One ticket keeps the fill simultaneous.
8. **Hold.** Typical holding is into a known event (earnings, FOMC), then exit. Expiry identities describe hold-to-$T$ P&L only. An early exit is a mark-to-market overlay this file does not specify.

## 6. Execution protocol

- Enter as a straddle (one ticket). Implied vol paid is the bet: you need a realized move $> D/S_0$ in relative terms, plus you fight theta.
- Default fill: next available after the chain is known. Delay-0 mid is research-only.
- Do not buy the call and the put on separate aggressive lifts unless the book can warehouse a one-legged long option.
- If you delta-hedge, expiry identities no longer describe P&L. Carry a separate Greek book.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings surprises as a signal (the event is a holding window, not an input to $f_T$).

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K$ | ATM, $K \approx S_0$ | listed strike nearest spot |
| tenor | 7–45 days | event vol; longer for vol-of-vol |
| quantity ratio | $1:1$ | call qty = put qty |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_straddle` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — same $K$ and expiry on both legs; qty $1:1$; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Theta.** Every day without a move bleeds $D$. A one-month ATM equity straddle can lose several percent of notional a week if spot sits still and implied vol does not rise.
- **IV crush.** $L_{\max}=D$ only at expiry; mark-to-market can be worse if you exit after implied vol collapses. Earnings straddles often die on the opening print even when the stock moved, because the move was smaller than the vol that was sold to you.
- **Wrong strike.** A far-from-ATM “straddle” is a strangle with a different debit and different break-evens. Treating it as this file silently widens the dead zone.
- **Pin.** $S_T=K$ realizes $L_{\max}$. Pin risk is real on names that attract option-market-maker hedges into expiry.
- **One-legged fill.** Buying only the call (or only the put) is a directional long option. The V identity is gone until the other wing is on.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K)_++(K-S_T)_+-D$ and also $|S_T-K|-D$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K$, $f_T=-L_{\max}=-D$. For $S_T>K+D$ or $S_T<K-D$, $f_T>0$.
- Reject a spec with unequal strikes, unequal expiries, or unequal quantities.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kink at $K$ except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
