---
rank: 15
slug: bull-call-spread
title: "Bull Call Spread"
asset_class: "options"
style: "directional bullish / debit vertical"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 015. Bull Call Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 15 of 101 |
| Why it sits here | The default defined-risk long call structure. First vertical every listed-options course teaches. |
| Aliases | — |
| Asset class | options |
| Style | directional bullish / debit vertical |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long a near-ATM call $K_1$, short an OTM call $K_2 > K_1$. Net debit. Profits if the stock rises into or above $K_2$. Capital-gain (not income) trade.

You are betting that $S_T$ finishes above $K_1+D$, ideally at or above $K_2$. You bought a call and sold a more expensive-to-reach call so the upside cannot exceed the width. You are not buying unlimited upside, and you are not collecting income: $D$ is a debit you lose if the name sits still or falls. You are also not running a covered call; there is no stock leg.

Payoff sketch, one lot, ignore financing: at $S_T=0$ both calls die and $f_T=-D=-L_{\max}$. At $S_T=K_1$ the long call is at the money and $f_T$ is still $-D$. At $S_T=K_2$ the width is fully earned and $f_T=K_2-K_1-D=P_{\max}$. Far above $K_2$ the same cap holds.

## 2. First principles

A long European call with strike $K_1$ pays

$$
(S_T - K_1)_+
$$

That is the engine. Below $K_1$ it is zero. Above $K_1$ it rises one-for-one. Alone it is an unlimited-upside debit. The spread exists to sell some of that upside for a smaller net debit.

A short European call with a higher strike $K_2>K_1$ pays

$$
-(S_T - K_2)_+
$$

Above $K_2$ this cancels further gain on the long call. Below $K_2$ it is zero. The short call is cheaper than the long call because it is further OTM (or less ITM). That gap is $D$.

The long call costs more than the short call brings in, so the package is a net debit $D$ at $t=0$. Adding the three pieces is the bull call spread:

$$
f_T = (S_T - K_1)_+ - (S_T - K_2)_+ - D
$$

$D$ must be less than $K_2-K_1$ or $P_{\max}$ is not positive. $D$ is two fills, not two mids. Below $K_1$ both calls die and you lose $D$. Between $K_1$ and $K_2$ the long call is in the money and the short is not, so P&L rises one-for-one with $S_T$. Above $K_2$ both calls are in the money and the width $K_2-K_1$ is fully earned, minus $D$. You bought a call and sold a more expensive-to-reach call so the upside cannot exceed that width.

That is the whole strategy. Everything below is just how to pick the two strikes, how to keep $D < K_2-K_1$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long-call strike, typically $K_1 \approx S_0$ |
| $K_2$ | short-call strike, $K_2 > K_1$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$. Structure so $D > 0$ and $D < K_2-K_1$.

## 4. Mathematics

### 4.1 Terminal payoff

Long call $K_1$ minus short call $K_2$, net debit $D$:

$$
f_T = (S_T - K_1)_+ - (S_T - K_2)_+ - D
$$

Two kinks, one debit. Tests must keep the signs: long the low strike, short the high strike. The opposite signs are a bear call spread (credit). Sketch: $S_T=0$ prints $-D$; at $K_1$ still $-D$; at $K_2$ and far above, $P_{\max}$.

### 4.2 Break-even

Set $f_T=0$ on $K_1 < S_T < K_2$, where $f_T = S_T-K_1-D$:

$$
S^\ast = K_1 + D
$$

The name must climb through the long strike by $D$. If $D$ is most of the width, $S^\ast$ sits just under $K_2$ and you need a near-complete rally to get paid anything. A cheap debit relative to width is a better $P_{\max}$, not automatically a better probability.

### 4.3 Extrema

Maximum profit is the width net of the debit, attained for $S_T \ge K_2$:

$$
P_{\max} = K_2 - K_1 - D
$$

A takeover print does not pay more than this. That is the point of selling $K_2$. Wider spreads cost more $D$ and pay more $P_{\max}$; they are a bigger directional bet, not a different shape.

Maximum loss is the debit, attained for $S_T \le K_1$:

$$
L_{\max} = D
$$

Sitting still or selling off loses $D$, not the width. Defined risk is the debit, not the short call. The short call only caps the right tail.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with two tight call strikes. Open interest on both legs above a minimum. A missing high strike leaves you long a naked call. Wide markets inflate $D$ and can push $D$ through the width.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K_1$ near ATM. A later print look-aheads moneyness and the debit.
3. **Strikes.** Buy $K_1 \approx S_0$, sell $K_2 > K_1$. Width $K_2-K_1$ typically 1–5% of spot for single stocks, or 10–50 index points for SPX. Width is $P_{\max}+D$. Choosing it is choosing how much rally you need.
4. **Expiry.** Same $T$, tenor 2–8 weeks. Mixed expiries are a diagonal, not this vertical. Short-dated verticals are more binary into the short strike.
5. **Size.** One long call and one short call per lot. Do not oversell the high strike. Extra shorts are a ratio spread, which is a different file with a different $L_{\max}$.
6. **Premium.** $D$ is the net debit actually paid. Reject if $D \ge K_2-K_1$ (no positive $P_{\max}$). That reject is a fill check, not a model check.
7. **Blotter.** Emit a two-legged net-debit vertical. Do not route live orders. One ticket keeps the long and the short together.
8. **Hold.** This spec is expiry-P&L. Practitioner exits at 50–75% of $P_{\max}$ are a separate overlay, not part of $f_T$. Early exit crystallizes a mark, including remaining time value on both calls.

## 6. Execution protocol

- Enter as a single vertical (one order, net debit limit). Do not leg in unless you can warehouse the long call.
- Prefer buying the long call between mid and ask; sell the short call at the bid or better inside the same ticket.
- American short-call assignment if the high strike goes ITM into an ex-date.
- Cap lots by ADV and by $D \times m$.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K_1$ | $\approx S_0$ | near-ATM long call |
| width $K_2-K_1$ | 1–5% of spot; 10–50 SPX points | listed strikes |
| tenor | 2–8 weeks | liquid cluster |
| quantity | $1:1$ | long $K_1$, short $K_2$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bull_call_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_2>K_1$; qty $1:1$; $D<K_2-K_1$; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined debit.** Sitting still loses $D$. A name that grinds sideways for six weeks into a near-ATM long call still prints $-D$ at expiry. This is a capital-gain trade; time is not your friend the way it is on a credit vertical.
- **Capped upside.** A rally through $K_2$ does not pay more than $P_{\max}$. A doubling after you sold a 5% OTM call still pays the width minus $D$.
- **Assignment.** American short call at $K_2$ can be exercised early. You can be short stock into an ex-date while still long the $K_1$ call, which is a conversion you did not ask for.
- **Wide $D$.** A fat debit relative to width leaves almost no $P_{\max}$. Paying $\$4.80$ for a $\$5$ wide spread is a lottery ticket with a $\$0.20$ top, not a conservative vertical.
- **Wrong signs.** Buying $K_2$ and selling $K_1$ is a bear call spread. The plateau becomes a credit you keep only if the name falls. Tests on $L_{\max}=D$ will catch it.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K_1)_+-(S_T-K_2)_+-D$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T\le K_1$, $f_T=-D=-L_{\max}$. For $S_T\ge K_2$, $f_T=K_2-K_1-D=P_{\max}$.
- Reject a spec with $K_2\le K_1$, unequal quantities, or $D\ge K_2-K_1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
