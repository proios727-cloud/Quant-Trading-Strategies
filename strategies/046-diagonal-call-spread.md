---
rank: 46
slug: diagonal-call-spread
title: "Diagonal Call Spread"
asset_class: "options"
style: "diagonal / bullish income"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 046. Diagonal Call Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 46 of 101 |
| Why it sits here | Poor-man’s covered call: long a deep ITM LEAP, short near-dated OTM calls. |
| Aliases | — |
| Asset class | options |
| Style | diagonal / bullish income |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long deep ITM call $K_1$ expiry $T'$, short OTM call $K_2$ expiry $T < T'$. Net debit. More protected against a squeeze than a calendar because the long more closely mimics stock.

You are betting that the LEAP behaves like a stock replacement and that you can sell OTM calls against it the way a covered-call book sells against shares. You are not holding stock, and you are not running a same-strike calendar: $K_1 \ne K_2$ is load-bearing. You are not running a European expiry identity in $S_T$ alone. The designed peak used below is the live mark of the LEAP when the short dies near $K_2$. Leftover LEAP premium can still go to zero without $S_T$ going to zero.

Payoff sketch, marked at the short expiry: at $S_T=0$ the short dies, the LEAP is a remaining cheap call, and $f_T$ is near $-D$ if that remnant is small. At $S_T=K_2$ the short dies worthless and $f_T=V-D$ when $V$ is the live LEAP mark (the usual peak case in this file). Far above $K_2$ you buy back the short at about $S_T-K_2$ while the LEAP is deep ITM; the extra intrinsic in $V$ may not cover the buy-back the way shares would in a covered call. $L_{\max}=D$ is an initial-debit bound, not a guaranteed live cap.

## 2. First principles

A short European call with OTM strike $K_2$ and expiry $T$ pays, at that expiry,

$$
-(S_T - K_2)_+
$$

That is a settled intrinsic, not a mark. Below $K_2$ it is zero. Above $K_2$ you owe $S_T-K_2$. The diagonal exists because you hope this piece is zero, or small, while a deep-ITM longer call still tracks the stock. A same-strike pair is a calendar, not this file.

A long European call with a lower strike $K_1<K_2$ and a later expiry $T'>T$ is still alive at $t=T$. It is not an intrinsic. Its mark $V(S_T)$ is the remaining value of the deep-ITM call (the LEAP):

$$
V(S_T) = C\bigl(S_T, K_1, T'-T\bigr)
$$

$V$ needs a vol surface or a listed mid at $t=T$. It is not $(S_T-K_1)_+$, though a 0.8-delta LEAP is close to that plus remaining premium. Using a surface fitted after $T$ look-aheads the mark. High delta is why this overlay is more stock-like than an ATM calendar.

The package is a net debit $D$ at $t=0$ because the LEAP costs more than the short OTM call brings in. Marked at the short expiry, the diagonal is

$$
f_T = V(S_T) - (S_T - K_2)_+ - D
$$

There is no simple closed $f_T$ in the spot alone: $V$ still has time value, and $K_1 \ne K_2$. After the short expires, the residual is a long ITM call — a stock replacement with residual downside to remaining premium, not to zero stock. The designed peak used below is the live mark of that LEAP when the short dies near its strike. A collapse can take $V$ toward remaining extrinsic, which can still be a large fraction of $D$. A rally through $K_2$ can cost more to buy back than a covered call would, because you do not deliver shares at $K_2$ unless you exercise the LEAP.

That is the whole strategy. Everything below is how to pick $K_1$, $K_2$, and the two expiries, how to roll the short, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at the short expiry $T$ |
| $K_1$ | long deep-ITM call strike, $K_1 < S_0$ |
| $K_2$ | short OTM call strike, $K_2 > S_0$ |
| $T$ | short-call expiry |
| $T'$ | long-call expiry, $T'>T$ |
| $V$ | mark of the long $K_1$ call at $t=T$ (live LEAP mark; peak case uses $S_T=K$ in the sense of the short-strike pin) |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | P&L marked at the short expiry, including $D$ |
| $P_{\max}$, $L_{\max}$ | max profit and max loss at that mark, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs are calls on the same underlying, quantity $1:1$, different strikes and expiries. Strike order: $K_2 > S_0 > K_1$.

## 4. Mathematics

### 4.1 Mark at the short expiry

The long call’s remaining value at $t=T$ is $V(S_T)$, a model or mid, not an intrinsic. The short call settles to $-(S_T-K_2)_+$. Net of the debit.

At $t=T$, let $V$ be the long call’s value if $S_T = K$ (use the live mark of the $K_1$ LEAP).

That $V$ is an input to `payoff` and `metrics`, not a number this file computes from $S_T$ alone. The "$K$" in the peak case is the short-strike pin in the sense of this file's notation note, not a third strike. Sketch: $S_T=0$ leaves a remaining cheap LEAP; $S_T=K_2$ is the usual peak $V-D$; far above $K_2$ the short's intrinsic can dominate the extra LEAP value versus a covered call.

### 4.2 Extrema

Maximum profit is that LEAP mark net of the debit:

$$
P_{\max} = V - D
$$

This is a mark, not a European expiry identity. If back-month IV has crushed, $V$ shrinks even on a friendly pin at $K_2$. If the LEAP is still rich and the short died, $P_{\max}$ is the poor-man's covered-call's whole point.

Maximum loss is the debit (the LEAP can go to remaining premium, not to a zero stock price; the bound used here is the initial debit):

$$
L_{\max} = D
$$

Treat $L_{\max}=D$ as cash spent, not as a guaranteed live floor. A short-call buy-back into a squeeze can print worse than $-D$ before you flatten. Residual LEAP downside is to remaining premium, which can be most of $D$ even if $S_T$ is not zero.

Roll the short if $S_{\mathrm{stop\text{-}loss}} \le S_T \le K_2$.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names with a deep-ITM longer-dated call and a near-dated OTM call. Open interest on both months above a minimum. A missing LEAP leaves you short a naked front call. A missing front is just a long LEAP.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K_1$ ITM and $K_2$ OTM. A later print look-aheads $D$ and both moneynesses.
3. **Long strike.** Buy $1$ deep ITM call $K_1<S_0$, delta $\approx 0.7$–$0.9$, expiry $T'$ of 3–12 months. Lower delta is a calendar in disguise. Higher delta costs more $D$ and tracks stock better. The LEAP is the stock replacement; that is why this step exists.
4. **Short strike.** Sell $1$ OTM call $K_2>S_0$, expiry $T$ of 2–6 weeks, $T<T'$. Further OTM collects less and keeps more LEAP upside. $T'<T$ is illegal. Same strike as $K_1$ would be a calendar, rejected by $K_2>S_0>K_1$.
5. **Premium.** $D$ is the net debit actually paid. A fat $D$ means you lifted the LEAP and sold the front poorly. Record fills, not mids.
6. **Blotter.** Emit a two-expiry, two-strike diagonal intent. Do not route live orders. One ticket keeps the front short from going on without the LEAP.
7. **Treat the long as a stock replacement.** Sell OTM calls against it on a covered-call schedule. That is the income engine. It is still not a covered call: leftover LEAP premium can go to zero without $S_T$ going to zero.
8. **Roll.** At $t=T$, if $S_{\mathrm{stop\text{-}loss}} \le S_T \le K_2$, sell the next short-dated OTM call. If $S_T \gg K_2$, buy back the short and reassess the LEAP. Rolling is a new credit against the same $D$ already spent, not a continuation of this $f_T$.

## 6. Execution protocol

- Enter as a diagonal (one ticket, net debit). Do not sell the front without the LEAP already on.
- $P_{\max}$ and $L_{\max}$ are marks at the short expiry, not European-expiry identities in $S_T$ alone. Carry a vol surface to evaluate $V$.
- More protected against a squeeze than a same-strike calendar because the long more closely mimics stock. It is still not a covered call: leftover LEAP premium can go to zero without $S_T$ going to zero.
- Cap lots by ADV on the tighter of the two months.

## 7. Data contract

Required, point-in-time, at $t=0$ and at $t=T$:

- Underlying last, bid, ask
- Option chain on **both** expiries: bid/ask, strike, expiry, call/put flag, open interest, implied vol (and delta to target $0.7$–$0.9$ on the long)
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates, and a vol surface or listed mid, to mark $V(S_T)$ at the short expiry

At the short expiry: underlying print, the short-call settlement, and the live mark of the $K_1$ LEAP. American early exercise on the short can invalidate the European roll.

Not used by this spec: stock borrow (no stock leg), book value, earnings as a signal.

No restatement peeking. Do not mark $V$ on a surface fitted through $t>T$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| long $K_1$ | deep ITM, delta $0.7$–$0.9$ | $K_1 < S_0$ |
| short $K_2$ | OTM | $K_2 > S_0$ |
| long tenor $T'$ | 3–12 months | LEAP or quarterlies |
| short tenor $T$ | 2–6 weeks | covered-call schedule |
| quantity | $1:1$ | both calls |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.diagonal_call_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec, long_mark) -> float` — $V(s_t) - (s_t-K_2)_+ - D$, with $V$ supplied as `long_mark`. There is no closed $f_T$ in $s_t$ alone.
4. `metrics(spec, V) -> dict` — `P_max`, `L_max` using $P_{\max}=V-D$ and $L_{\max}=D$.
5. `validate(spec)` — $K_2>S_0>K_1$; $T'<T$ rejected; qty $1:1$; both rights are calls.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Residual LEAP downside.** The long option still has residual downside to its remaining premium (not to zero stock). A 30% decline can take a 0.8-delta LEAP down by far more than the front credit you collected, even though $S_T$ is not zero.
- **Vol crush on the LEAP.** Back-month IV can fall while the short expires, eating $V$. Earnings diagonals often die on the LEAP crush the same way calendars do.
- **Rally through $K_2$.** Buying back the short ITM can cost more than the LEAP’s remaining extra value versus a covered call. You cannot deliver shares at $K_2$ unless you exercise, which throws away remaining LEAP time value.
- **Wrong $V$.** Using a stale surface look-aheads the mark. Research that always prints $P_{\max}$ on a pin is often this bug.
- **American assignment.** Early exercise on the front call into an ex-date leaves you short stock against a LEAP, which is a conversion you did not ask for.

## 11. Acceptance tests

- `metrics` reports $P_{\max}=V-D$ and $L_{\max}=D$ when $V$ is the supplied LEAP mark.
- Reject a spec with $T'\le T$, $K_1\ge K_2$, a put leg, or unequal quantities.
- `validate` requires $K_2 > S_0 > K_1$.
- Permuting quotes after $t=0$ must not change the recorded $D$.
- Adding a fee $\tau$ per contract shifts the mark by a constant and does not change $K_1$ or $K_2$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
