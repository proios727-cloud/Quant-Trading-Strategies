---
rank: 66
slug: calendar-put-spread
title: "Calendar Put Spread"
asset_class: "options"
style: "horizontal / mildly bearish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 066. Calendar Put Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 66 of 101 |
| Why it sits here | Put-side calendar; covered-put analogue without short stock. |
| Aliases | — |
| Asset class | options |
| Style | horizontal / mildly bearish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long a near-ATM put with expiry $T'$ and short a same-strike put with earlier expiry $T < T'$. Net debit. Best case at the short expiry: $S_T = K$. The structure is the put-side analogue of a calendar call, and can be rolled like a covered put without holding short stock.

You are betting that spot stays near $K$ into the front expiry, so the short put dies and the back-month put keeps time value $V$. You are not betting on a crash. A large down move into $T$ is the dangerous path: the short put’s intrinsic can outrun the long put’s remaining mark. You are also not running a directional short-stock book; there is no share leg unless assignment forces one.

The typical user wants put-calendar income, or a covered-put overlay without locating borrow. Horizon is two-clock: mark and manage at the front expiry $T$, then either roll another short put against the residual long or flatten. If either expiry lacks a two-sided market at $K$, skip the name.

A net credit calendar (back month cheaper than front) is not this spec unless you are explicitly selling back-month vol. Default is a debit $D>0$. Size off the thinner of the two expiries and off crash-through-$K$ P&L, not off $D$ alone.

## 2. First principles

Two listed puts, same strike $K$, different expiries. At inception you pay net debit $D$ for long $T'$ minus short $T$. The long costs more because it has more calendar. That extra calendar is what you are buying; the short front put is how you finance it and how you pin the peak.

At the front expiry $t=T$ the short put settles to intrinsic:

$$
-(K - S_T)_+
$$

The front leg is dead after $T$. If $S_T \ge K$ this term is zero and you kept the credit from that sale. If $S_T < K$ you owe $K-S_T$. That owed amount is not automatically offset by the long put, because the long still has time left and is marked, not settled.

The long put is still alive. Write $V(S_T)$ for its mark at $t=T$ (remaining time value plus intrinsic). Front-expiry P&L is the sum of those two legs minus the opening debit:

$$
f_T = V(S_T) - (K - S_T)_+ - D
$$

There is no simple closed $f_T$ in the spot alone, because $V$ still has time value. $V$ must come from a live mid or a model on a surface dated $\le T$. If you plug in the long put’s *eventual* expiry intrinsic at $T'$, you look ahead and overstate the hedge on a crash. If you set $V=0$ whenever $S_T \ge K$, you understate the pin profit.

The best case is $S_T = K$: the short expires worthless and the long is an ATM remaining put with value $V$. That is the peak:

$$
P_{\max} = V - D
$$

$V$ here is $V(K)$, the ATM remaining mark, not a guess. If term-structure vol crushes, $V$ can be smaller than the debit and the “peak” is a loss. $P_{\max}$ is therefore a mark at $t=T$, not a guaranteed coupon. Skipping the $V$ input and reporting $P_{\max}$ as a function of $S_T$ only is a spec violation.

If the front put finishes worthless and the back put is also crushed ($S_T \gg K$), you lose the debit. If you never recover more than you paid:

$$
L_{\max} = D
$$

That bound is the quiet-tape / rally bound: both puts die and you are out the debit. It is **not** a hard crash bound. A gap through $K$ into the short expiry can print worse than $-D$ until the long put’s mark catches up, especially on American assignment.

After the short expires, the residual is a long put. You can sell another front-month put against it when spot stays near $K$. That is the income overlay, symmetric to rolling a calendar call. Rolling without the long still on is a naked short put. Rolling after $S_T \ll K$ without buying back the short is how assignment shows up in the blotter.

**Payoff sketch (at the front expiry).** Same $K$, debit $D$. At $S_T=K$, $f_T=V-D$ (the design peak). At $S_T$ far above $K$, $V\to 0$ and $f_T\to -D$. At $S_T=0$, the short put is worth $K$ and the long put’s mark is a remaining deep-ITM put, so P&L is $V(0)-K-D$, which can be worse than $-D$ on a gap. The sketch is a hill at $K$, not a crash payoff.

That is the whole strategy. You are fading a move away from $K$ into the short expiry, not buying a directional crash.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at the **front** expiry $T$ |
| $K$ | common strike, $K \approx S_0$ |
| $T < T'$ | front and back put expiries |
| $V$ | mark of the long $T'$ put at $t=T$ when $S_T = K$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | P&L at the front expiry, including $D$ |
| $S_{\mathrm{stop\text{-}loss}}$ | roll/exit band above $K$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss evaluated at $t=T$ |

One long back-month put, one short front-month put. Same $K$. Quantity ratio $1:1$.

## 4. Mathematics

### 4.1 Premium

Net debit $D > 0$: the back-month put costs more than the front-month put brings in. If the calendar is a credit, the back month is cheaper than the front — that is a vol-term-structure sale, not this file. Record $D$ from wing/front asks and bids, not from mids.

### 4.2 Front-expiry mark

With $V(S_T)$ the live mark of the long put at $t=T$:

$$
f_T = V(S_T) - (K - S_T)_+ - D
$$

This is a *mark* identity, not a European expiry identity in $S_T$ alone. Tests must take a supplied `back_mark`. When $S_T = K$, write $V = V(K)$ for that ATM remaining value. A surface fitted through prints after $T$ is look-ahead.

### 4.3 Max profit and loss

Peak at the pin $S_T = K$:

$$
P_{\max} = V - D
$$

That is the number you store in metrics, using a pricing mark for $V$. If $V<D$, the structure cannot profit at the pin on that mark; reject or size down. $P_{\max}$ moves when the back-month IV moves, even if spot pins.

Debit at risk if the remaining put is worth nothing after the short expires:

$$
L_{\max} = D
$$

A crash through $K$ into the short expiry is the dangerous path: the short put’s intrinsic can outrun the long put’s mark, so realized P&L can be worse than $-D$ until the long catches up. $L_{\max}=D$ is the **quiet-tape** bound, not a hard crash bound. Risk limits that treat $D$ as max loss will be wrong on a gap.

### 4.4 Roll region

After the short expires, residual is a long put. Roll another short put with expiry $T_1 < T'$ at the same $K$ when

$$
K \le S_T \le S_{\mathrm{stop\text{-}loss}}
$$

The band is “spot still near the strike, not yet a rally that killed the long.” Below $K$ you are in assignment territory on the old short; do not sell a new short until that is cleaned up. Above $S_{\mathrm{stop\text{-}loss}}$ the residual long put is decaying — flatten or accept the debit. The roll exists to repeat the income overlay, not to average a losing calendar.

### 4.5 Mark-to-market

Before $T$, mark is the sum of option mids minus initial $D$. $P_{\max}$ / $L_{\max}$ are **front-expiry** quantities. Delta-hedging replaces this identity with a Greek book $\Delta, \Gamma, \Theta, \nu$. Calendar P&L is mostly term-structure of vol plus pin at $K$. A backtest that holds to $T'$ without marking at $T$ is a different strategy.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed puts on one underlying. Both expiries must have a posted bid/ask at $K$. Without two live markets you cannot compute a real $D$ or a real $V$.
2. **Strikes and tenors.** $K \approx S_0$. Front $T$ in 1–4 weeks, back $T'$ in 1–3 months, $T < T'$. The gap in tenor is the calendar you are buying; $T \ge T'$ is invalid.
3. **Legs.** Buy 1 put expiry $T'$, sell 1 put expiry $T$, same $K$. Quantity ratio $1:1$. A ratio or a strike mismatch is a diagonal or a ratio spread.
4. **Premium.** Require $D>0$ and $D$ small versus a model $V$ at $S_T=K$. Reject inverted calendars that are a net credit unless you are explicitly selling back-month vol. This check is how you keep the file a debit calendar.
5. **Metrics.** Store $P_{\max}=V-D$ using a pricing mark for $V$, and $L_{\max}=D$. There is no closed $S^\ast$ in $S_T$ alone; do not invent one.
6. **Blotter.** Emit a two-expiry put calendar intent. Do not route live orders. One ticket, net-debit limit.
7. **At $T$.** If $K \le S_T \le S_{\mathrm{stop\text{-}loss}}$, sell another front put; else flatten or hold the residual long put. Do not keep a naked short put after the long is gone. This step is the covered-put engine.

## 6. Execution protocol

- Enter as one calendar (one ticket, net-debit limit). Symmetric to the calendar call. Legging the short first is a naked put.
- Income engine: roll short puts while $S$ stays near $K$, as you would roll a covered put without locating stock. If you skip the roll band and keep selling puts after a rally, you are writing puts against a dying long.
- If $S_T \ll K$ into the short expiry, buy back the short before assignment; the long put has not fully caught up. Treating $-D$ as the worst print on that path is how the backtest lies.
- Cap size by the thinner of the two expiries’ open interest, not by $D$ alone.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain **on two expiries** $T$ and $T'$: bid/ask, strike, call/put flag, open interest, implied vol, multiplier
- A pricing mark (or live mid) for the back-month put at $t=T$, used as $V(S_T)$
- Dividends and rates if $V$ is model-based
- At each expiry: settlement print and American early-exercise events

Not used by this spec: book value, earnings, SUE, a stock borrow tape (no stock leg).

These identities treat the long option as a European-style remaining claim. American early exercise on the short put can invalidate the roll. Do not mark $V$ on a surface that uses prints after $T$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K$ | ATM, $K \approx S_0$ | same strike both expiries |
| front tenor $T$ | 1–4 weeks | short put |
| back tenor $T'$ | 1–3 months | long put |
| quantity ratio | $1:1$ | one long, one short |
| $S_{\mathrm{stop\text{-}loss}}$ | caller-set | roll band above $K$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.calendar_put_spread` with:

1. `legs(spec) -> list[Leg]` — long put $T'$, short put $T < T'$, same $K$, qty $1:1$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive); debit $D$ is the negative of that credit.
3. `payoff(s_t, spec, back_mark) -> float` — implements $f_T = V(S_T) - (K-S_T)_+ - D$.
4. `metrics(spec, V) -> dict` — `P_max`, `L_max`, debit flag; no closed $S^\ast$ in $S_T$ alone.
5. `validate(spec)` — $T < T'$, same $K$, qty $1:1$, $D>0$.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Crash through $K$ into the short expiry.** Short-put assignment versus a long put that has not fully caught up. Realized loss can exceed $D$ intra-day. A gap to $0$ is the concrete stress, not a slow drift.
- **Vol term structure.** Back-month IV can crush more than the front, shrinking $V$ even if spot pins $K$. Then $P_{\max}=V-D$ is small or negative and the “best case” is a loss.
- **Rally.** Both puts die; you lose $D$. That is the designed max loss on a quiet-to-up tape, and it is how most calendars actually expire.
- **Pin / assignment.** American short put near $K$ into expiry can force a stock short you did not locate.
- **Look-ahead $V$.** Marking the back put with a surface fitted after $T$ invents pin profit the live tape never paid.

## 11. Acceptance tests

- At $S_T = K$, $f_T = V - D = P_{\max}$ when `back_mark` $= V$.
- If $V(S_T)=0$ for $S_T \ge K$, then $f_T = -D = -L_{\max}$.
- Reject $T \ge T'$, mismatched strikes, or quantity ratio other than $1:1$.
- Grid of $S_T$ plus a supplied $V(S_T)$: $f_T$ equals the listed-leg mark minus $D$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant through $D$, and does not change $K$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
