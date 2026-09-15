---
rank: 17
slug: calendar-call-spread
title: "Calendar Call Spread"
asset_class: "options"
style: "horizontal / theta / mildly bullish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 017. Calendar Call Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 17 of 101 |
| Why it sits here | Core time-spread. Used as a vol-term-structure trade and as a covered-call analogue without holding stock. |
| Aliases | — |
| Asset class | options |
| Style | horizontal / theta / mildly bullish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long a near-ATM call with expiry $T'$ and short a same-strike call with earlier expiry $T < T'$. Net debit. Best case at the short expiry: $S_T = K$. Can be rolled like a covered call.

You are betting that at the front expiry the stock sits near $K$, so the short call dies and the back-month call still has time value $V$. You are not betting on a large rally or a crash: both pull the long call's remaining value in ways that often fail to cover buying back the short. You are not holding stock, and you are not running a European expiry identity in $S_T$ alone. The designed peak is a pin at $K$. Term-structure of vol is first-order: a crush in the back month can erase $V$ even if spot cooperates.

Payoff sketch, marked at the short expiry: at $S_T=0$ the short dies, the long is a far-OTM remaining call, and $f_T \approx -D$ if that remnant is near zero. At $S_T=K$ the short dies worthless and $f_T=V-D=P_{\max}$ when $V$ is the ATM back-month mark. Far above $K$ you buy back the short at about $S_T-K$ while the long is a deep-ITM remaining call; the difference can be less than $D$, so $L_{\max}=D$ is an initial-debit bound, not a guaranteed live cap.

## 2. First principles

A short European call with strike $K$ and expiry $T$ pays, at that expiry,

$$
-(S_T - K)_+
$$

That is a settled intrinsic, not a mark. Below $K$ it is zero. Above $K$ you owe $S_T-K$. The calendar exists because you hope this piece is zero, or small, while the longer call still has time value. Same strike is load-bearing; a different short strike is a diagonal.

A long European call with the same strike and a later expiry $T'>T$ is still alive at $t=T$. It is not an intrinsic. Its mark $V(S_T)$ is the remaining time value plus any intrinsic:

$$
V(S_T) = C\bigl(S_T, K, T'-T\bigr)
$$

$V$ needs a vol surface or a listed mid at $t=T$. It is not $(S_T-K)_+$. Using a surface fitted after $T$ look-aheads the mark. Using delay-0 mid after the print is the same sin. $V$ is largest near ATM, which is why the peak is at $S_T=K$.

The package is a net debit $D$ at $t=0$ because the back-month call costs more than the front-month credit. Marked at the short expiry, the calendar is

$$
f_T = V(S_T) - (S_T - K)_+ - D
$$

There is no simple closed $f_T$ in the spot alone: $V$ still has time value. After the short expires, the residual is a long call. The designed peak is at $S_T=K$, where the short dies worthless and $V$ is the ATM back-month mark. A sharp rally forces a buy-back of the short that can exceed the extra intrinsic in $V$. A collapse can leave $V$ near zero. Both paths can realize something close to $-D$.

That is the whole strategy. Everything below is how to pick $K$ and the two expiries, how to roll the short, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at the short expiry $T$ |
| $K$ | common strike, $K \approx S_0$ |
| $T$ | short-call expiry |
| $T'$ | long-call expiry, $T'>T$ |
| $V$ | mark of the long call at $t=T$ when $S_T=K$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | P&L marked at the short expiry, including $D$ |
| $P_{\max}$, $L_{\max}$ | max profit and max loss at that mark, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs are calls on the same underlying, quantity $1:1$, same $K$, different expiries.

## 4. Mathematics

### 4.1 Mark at the short expiry

The long call’s remaining value at $t=T$ is $V(S_T)$, a model or mid, not an intrinsic. The short call settles to $-(S_T-K)_+$. Net of the debit:

the peak case used below is the ATM mark of that long call. Let $V$ be the value of the long call at $t=T$ if $S_T = K$.

That $V$ is an input to `payoff` and `metrics`, not a number this file computes from $S_T$ alone. Supplying a stale $V$ is a look-ahead if the surface used prints after $T$. Sketch: $S_T=0$ leaves a cheap remaining OTM call; $S_T=K$ is the designed peak $V-D$; far above $K$ the short's intrinsic can dominate.

### 4.2 Extrema

Maximum profit is that ATM back-month mark net of the debit:

$$
P_{\max} = V - D
$$

This is a mark, not a European expiry identity. If implied vol in the back month has crushed, $V$ is small and $P_{\max}$ shrinks even on a perfect pin. If the back month is rich, $P_{\max}$ is the calendar's whole point.

Maximum loss is the debit (the back-month call can go to zero after a collapse, and a sharp rally can force a buy-back of the short above the long’s remaining value; the bound used here is the initial debit):

$$
L_{\max} = D
$$

Treat $L_{\max}=D$ as an accounting bound on cash spent, not as a guaranteed live floor. A short-call buy-back into a squeeze can print worse than $-D$ before you flatten. After the short expires, residual is a long call with its own remaining debit.

There is no simple closed $f_T$ in the spot alone because the long option still has time value. After the short expires, residual is a long call.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with two expiries at the same $K$. Open interest on both months above a minimum. A missing back month leaves you short a naked front call. A missing front month is just a long call.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K$ near ATM. A later print look-aheads the debit and the intended pin.
3. **Strike.** Choose $K \approx S_0$ (ATM calendar). An OTM calendar is a different bet (you want a rally toward $K$). An ITM calendar behaves more like a debit diagonal. This file's peak identity uses ATM $V$.
4. **Expiries.** Front tenor $T$ of 1–4 weeks; back tenor $T'$ of 1–3 months; $T'<T$ is illegal. The front must die first. A pair with $T'=T$ is not a calendar.
5. **Size.** Buy $1$ call expiry $T'$, sell $1$ call expiry $T$, same $K$. Ratioing the front is a different short-gamma book. Lot integrity is $1:1$.
6. **Premium.** $D$ is the net debit actually paid. A tiny $D$ with a rich back month is the usual listed calendar. A fat $D$ means the front credit was poor or the back was lifted.
7. **Blotter.** Emit a two-expiry calendar intent. Do not route live orders. One ticket keeps the front short from going on without the back.
8. **Roll.** At $t=T$, if $S_{\mathrm{stop\text{-}loss}} \le S_T \le K$, sell another call with expiry $T_1 < T'$ at the same $K$. That is the income overlay, analogous to a covered call. If $S_T \gg K$, buy back the short and reassess the long. Rolling is a new trade with a new credit, not a continuation of this $f_T$.

## 6. Execution protocol

- Enter as a calendar (one ticket, net debit). Do not sell the front without the back already on.
- $P_{\max}$ and $L_{\max}$ are marks at the short expiry, not European-expiry identities in $S_T$ alone. Carry a vol surface to evaluate $V$.
- Term-structure of vol can crush the back month more than the front earns in theta; that is a first-order P&L driver, not a residual.
- Cap lots by ADV on the tighter of the two months.

## 7. Data contract

Required, point-in-time, at $t=0$ and at $t=T$:

- Underlying last, bid, ask
- Option chain on **both** expiries: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates, and a vol surface or listed mid, to mark $V(S_T)$ at the short expiry

At the short expiry: underlying print, the short-call settlement, and the live mark of the long call. American early exercise on the short can invalidate the European roll.

Not used by this spec: stock borrow (no stock leg), book value, earnings as a signal.

No restatement peeking. Do not mark $V$ on a surface fitted through $t>T$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K$ | ATM, $K \approx S_0$ | same strike both months |
| front tenor $T$ | 1–4 weeks | short call |
| back tenor $T'$ | 1–3 months | long call |
| quantity | $1:1$ | same $K$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.calendar_call_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec, long_mark) -> float` — $V(s_t) - (s_t-K)_+ - D$, with $V$ supplied as `long_mark`. There is no closed $f_T$ in $s_t$ alone.
4. `metrics(spec, V) -> dict` — `P_max`, `L_max` using $P_{\max}=V-D$ and $L_{\max}=D$ when $V$ is the ATM mark at $t=T$.
5. `validate(spec)` — same $K$; $T'<T$ rejected; qty $1:1$; both rights are calls.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Term-structure crush.** The back month can lose more vega than the front earns in theta. An earnings-week calendar that sells the front and holds the back through the event often dies on the back-month crush even if $S_T\approx K$.
- **Rally through $K$.** Buying back the short ITM can cost more than the long’s remaining value; $L_{\max}=D$ is the initial-debit bound, not a guaranteed live cap. A gap 15% through $K$ the day before the front expiry is the usual example.
- **Wrong $V$.** Using a stale surface or a delay-0 mid after $T$ look-aheads the mark. Research that "always pins and always makes $P_{\max}$" is often this bug.
- **Pin then roll.** Rolling only when $S_T\le K$ is a rule, not an identity. Rolling into a new short after a near-miss pin starts a new $D$ and a new assignment clock.
- **American assignment.** Early exercise on the front call into an ex-date leaves you short stock against a back-month call, which is a conversion you did not ask for.

## 11. Acceptance tests

- At $S_T=K$, `payoff` equals $V-D=P_{\max}$ when `long_mark` is that ATM $V$.
- `metrics` reports $L_{\max}=D$ and $P_{\max}=V-D$.
- Reject a spec with $T' \le T$, different strikes, unequal quantities, or a put leg.
- Permuting quotes after $t=0$ must not change the recorded $D$.
- Adding a fee $\tau$ per contract shifts the mark by a constant and does not change $K$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
