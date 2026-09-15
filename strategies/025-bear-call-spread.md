---
rank: 25
slug: bear-call-spread
title: "Bear Call Spread"
asset_class: "options"
style: "bearish income / credit vertical"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 025. Bear Call Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 25 of 101 |
| Why it sits here | Credit-vertical counterpart of the bull put spread. The call side of an iron condor. |
| Aliases | — |
| Asset class | options |
| Style | bearish income / credit vertical |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long OTM call $K_1$, short lower-strike OTM call $K_2 < K_1$. Net credit. Income if the stock stays below $K_2$.

You are betting that $S_T$ finishes at or below $K_2$ so both calls die and you keep $C$. You sold a call and bought a further-OTM call so the loss cannot exceed the width. You are not running a naked short call, and you are not buying a bullish debit vertical. Tiny $C$ versus width is a bad payoff, not a safer one. This vertical is often the call side of a credit iron condor.

Payoff sketch, one lot, ignore financing: at $S_T=0$ both calls die and $f_T=C=P_{\max}$. At $S_T=K_2$ the short call is at the money and $f_T$ is still $C$. At $S_T=K_1$ the width is fully lost and $f_T=C-(K_1-K_2)=-L_{\max}$. Far above $K_1$ the same cap holds.

## 2. First principles

A long European call with the higher strike $K_1$ pays

$$
(S_T - K_1)_+
$$

That is the wing. Above $K_1$ it pays $S_T-K_1$. Below $K_1$ it is zero. You buy it so a rally cannot take more than the width on this vertical. Without it this file is a naked short call.

A short European call with the lower strike $K_2<K_1$ pays

$$
-(S_T - K_2)_+
$$

That is the income engine. Above $K_2$ it costs $S_T-K_2$. Below $K_2$ it is zero. The short call is closer to the money, so it is worth more than the wing. That gap is $C$.

The short call is closer to the money, so it brings in more premium than the long call costs. The package is a net credit $C$ at $t=0$. Adding the three pieces is the bear call spread:

$$
f_T = (S_T - K_1)_+ - (S_T - K_2)_+ + C
$$

$C$ must be less than $K_1-K_2$ or there is no room for a positive $P_{\max}$ after a complete width loss. $C$ is two fills, not two mids. Below $K_2$ both calls die and you keep $C$. Between $K_2$ and $K_1$ the short call is in the money and the long is not, so P&L falls as $S_T$ rises. Above $K_1$ both calls are in the money and the loss is the width $K_1-K_2$ minus $C$. You sold a call and bought a further-OTM call so the loss cannot exceed that width.

That is the whole strategy. Everything below is how to pick the two strikes, how to keep $C < K_1-K_2$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long OTM call strike |
| $K_2$ | short OTM call strike, $K_2 < K_1$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$. Typically both strikes are OTM, $K_2 > S_0$. Structure so $C < K_1-K_2$.

## 4. Mathematics

### 4.1 Terminal payoff

Long call $K_1$ minus short call $K_2$, net credit $C$:

$$
f_T = (S_T - K_1)_+ - (S_T - K_2)_+ + C
$$

Credit, not debit. Tests must keep the signs: long the high strike, short the low strike. The opposite signs are a bull call spread. Sketch: $S_T=0$ prints $C$; at $K_1$ and far above, $-L_{\max}$.

### 4.2 Break-even

Set $f_T=0$ on $K_2 < S_T < K_1$, where $f_T = C - (S_T-K_2)$:

$$
S^\ast = K_2 + C
$$

A rally of $C$ through the short strike eats the credit. Above $S^\ast$ you lose until the long call at $K_1$ stops the bleed. If $C$ is small relative to width, most of the wing is a losing region.

### 4.3 Extrema

Maximum profit is the credit, attained for $S_T \le K_2$:

$$
P_{\max} = C
$$

Sitting still below the short strike is the designed outcome. Time is on your side the way it is not on a debit call spread. Mark-to-market can still be negative on that path if implied vol rises.

Maximum loss is the width net of the credit, attained for $S_T \ge K_1$:

$$
L_{\max} = K_1 - K_2 - C
$$

A complete test of the wing realizes this number. For a $\$5$ wide call spread and a $\$1$ credit, $L_{\max}=\$4$ per share, times $m$. Defined is not small. A takeover print still pays only this cap, which is the point of the long wing.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with two tight call strikes. Open interest on both legs above a minimum. A missing long wing is a naked short call. Wide call markets shrink $C$.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. Default structure wants $K_2>S_0$. A later print can put the short strike ITM and look-ahead $C$.
3. **Strikes.** Sell call $K_2$, buy call $K_1>K_2$, both OTM. Short strike typically 16–30 delta. Closer shorts collect more $C$ and get tested more. Width is $L_{\max}+C$.
4. **Expiry.** Same $T$. Typical 1 week to 3 months. Mixed expiries are a diagonal, not this vertical. Short-dated credit calls harvest theta and take dividend-assignment risk into expiry.
5. **Size.** One short call and one long call per lot. Extra shorts without extra longs are a ratio call spread with a different $L_{\max}$.
6. **Premium.** $C$ is the net credit actually received. Reject if $C \ge K_1-K_2$. That reject is a fill check.
7. **Blotter.** Emit a two-legged net-credit vertical. Do not route live orders. One ticket keeps the short from going on without the wing.
8. **Hold.** Defined risk. Pair with a bull put spread to form a long (credit) iron condor. Early management at 50% of credit is an overlay, not part of $f_T$.

## 6. Execution protocol

- Enter as a net-credit vertical (one ticket). Do not sell $K_2$ without $K_1$ already on.
- American short-call assignment if $K_2$ is ITM, especially into an ex-date.
- Cap lots by $L_{\max}\times m$ and by ADV.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol (and delta if you select the short strike by delta)
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| short strike $K_2$ | 16–30 delta | OTM call |
| width $K_1-K_2$ | 1–5% of spot | listed strikes |
| tenor | 1 week to 3 months | income cluster |
| quantity | $1:1$ | long $K_1$, short $K_2$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bear_call_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1>K_2$; qty $1:1$; $C<K_1-K_2$; $P_{\max}=C$ and $L_{\max}=K_1-K_2-C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined rally.** A print through both strikes loses $L_{\max}$. A takeover or a 15% squeeze against a 5% wide, 16-delta short call still takes the whole width minus $C$, times $m$.
- **Assignment.** The short call at $K_2$ can be exercised early, especially into an ex-date. You wake up short stock, still long the $K_1$ call.
- **Credit too small.** Tiny $C$ versus width is a bad payoff, not a safer one. Collecting $\$0.20$ on a $\$5$ wing is selling a lottery for almost nothing.
- **Wrong sign.** Buying $K_2$ and selling $K_1$ is a bull call spread, not this file. You would then need the name to rally. Tests on $P_{\max}=C$ at low $S_T$ will catch the flip.
- **Dividend assignment.** Index names are cleaner. Single-stock credit calls into a large ex-date are where the European identity quietly dies.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K_1)_+-(S_T-K_2)_++C$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T\le K_2$, $f_T=C=P_{\max}$. For $S_T\ge K_1$, $f_T=C-(K_1-K_2)=-L_{\max}$.
- Reject a spec with $K_1\le K_2$, unequal quantities, or $C\ge K_1-K_2$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
