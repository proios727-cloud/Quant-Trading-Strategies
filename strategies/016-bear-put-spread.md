---
rank: 16
slug: bear-put-spread
title: "Bear Put Spread"
asset_class: "options"
style: "directional bearish / debit vertical"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 016. Bear Put Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 16 of 101 |
| Why it sits here | The defined-risk bearish counterpart of the bull call spread. Equally standard. |
| Aliases | — |
| Asset class | options |
| Style | directional bearish / debit vertical |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long a near-ATM put $K_1$, short an OTM put $K_2 < K_1$. Net debit. Profits if the stock falls.

You are betting that $S_T$ finishes below $K_1-D$, ideally at or below $K_2$. You bought a put and sold a cheaper, further-OTM put so the downside gain cannot exceed the width. You are not buying a naked crash lottery, and you are not collecting income: $D$ is a debit you lose if the name rallies or sits still. You are also not short the stock; there is no stock leg.

Payoff sketch, one lot, ignore financing: at $S_T=0$ both puts are in the money and $f_T=K_1-K_2-D=P_{\max}$. At $S_T=K_2$ the short put is at the money and the width is fully earned, still $P_{\max}$. At $S_T=K_1$ the long put dies and $f_T=-D=-L_{\max}$. Far above $K_1$ both puts are dead and $f_T$ stays $-D$.

## 2. First principles

A long European put with strike $K_1$ pays

$$
(K_1 - S_T)_+
$$

That is the engine. Above $K_1$ it is zero. Below $K_1$ it rises one-for-one as $S_T$ falls. Alone it is an almost-unlimited downside debit (capped at $K_1$ if the stock goes to zero). The spread exists to sell some of that tail for a smaller net debit.

A short European put with a lower strike $K_2<K_1$ pays

$$
-(K_2 - S_T)_+
$$

Below $K_2$ this cancels further gain on the long put. Above $K_2$ it is zero. The short put is cheaper because it is further OTM. That gap is $D$.

The long put costs more than the short put brings in, so the package is a net debit $D$ at $t=0$. Adding the three pieces is the bear put spread:

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ - D
$$

$D$ must be less than $K_1-K_2$ or $P_{\max}$ is not positive. $D$ is two fills, not two mids. Above $K_1$ both puts die and you lose $D$. Between $K_2$ and $K_1$ the long put is in the money and the short is not, so P&L rises as $S_T$ falls. Below $K_2$ both puts are in the money and the width $K_1-K_2$ is fully earned, minus $D$. You bought a put and sold a cheaper, further-OTM put so the downside gain cannot exceed that width.

That is the whole strategy. Everything below is just how to pick the two strikes, how to keep $D < K_1-K_2$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long-put strike, typically $K_1 \approx S_0$ |
| $K_2$ | short-put strike, $K_2 < K_1$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$. Structure so $D > 0$ and $D < K_1-K_2$.

## 4. Mathematics

### 4.1 Terminal payoff

Long put $K_1$ minus short put $K_2$, net debit $D$:

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ - D
$$

Two kinks, one debit. Tests must keep the signs: long the high strike, short the low strike. The opposite signs are a bull put spread (credit). Sketch: $S_T=0$ prints $P_{\max}$; at $K_2$ still $P_{\max}$; at $K_1$ and far above, $-D$.

### 4.2 Break-even

Set $f_T=0$ on $K_2 < S_T < K_1$, where $f_T = K_1-S_T-D$:

$$
S^\ast = K_1 - D
$$

The name must fall through the long strike by $D$. If $D$ is most of the width, $S^\ast$ sits just above $K_2$ and you need a near-complete drop to get paid anything. Skew often makes put verticals more expensive than the matching call vertical; $D$ is larger and $P_{\max}$ is smaller for the same width.

### 4.3 Extrema

Maximum profit is the width net of the debit, attained for $S_T \le K_2$:

$$
P_{\max} = K_1 - K_2 - D
$$

A bankruptcy print does not pay more than this. That is the point of selling $K_2$. The stock going to zero and the stock going to $K_2$ pay the same at expiry.

Maximum loss is the debit, attained for $S_T \ge K_1$:

$$
L_{\max} = D
$$

A rally through $K_1$ loses $D$, not the width. Defined risk is the debit. The short put only caps the left tail of the long put.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with two tight put strikes. Open interest on both legs above a minimum. A missing low strike leaves you long a naked put. Wide put markets, especially on single names into events, inflate $D$.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K_1$ near ATM. A later print look-aheads moneyness and the debit.
3. **Strikes.** Buy $K_1 \approx S_0$, sell $K_2 < K_1$. Width $K_1-K_2$ typically 1–5% of spot for single stocks, or 10–50 index points for SPX (same guidance as the bull call spread). Width is $P_{\max}+D$. Choosing it is choosing how much decline you need.
4. **Expiry.** Same $T$, tenor 2–8 weeks. Mixed expiries are a diagonal put spread, not this vertical.
5. **Size.** One long put and one short put per lot. Extra shorts are a ratio put spread, a different $L_{\max}$.
6. **Premium.** $D$ is the net debit actually paid. Reject if $D \ge K_1-K_2$. That reject is a fill check. Skew can make a listed put vertical fail this check when the matching call vertical would pass.
7. **Blotter.** Emit a two-legged net-debit vertical. Do not route live orders. One ticket keeps both puts together.
8. **Hold.** This spec is expiry-P&L. No stock leg is required. Early profit-taking is an overlay, not part of $f_T$.

## 6. Execution protocol

- Enter as a net-debit vertical (one ticket). Do not leg in unless you can warehouse the long put.
- Watch hard-to-borrow on the underlying only if you also short stock; this trade does not require stock.
- American short-put assignment if $K_2$ is ITM.
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
| $K_1$ | $\approx S_0$ | near-ATM long put |
| width $K_1-K_2$ | 1–5% of spot; 10–50 SPX points | same as bull call spread |
| tenor | 2–8 weeks | liquid cluster |
| quantity | $1:1$ | long $K_1$, short $K_2$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bear_put_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1>K_2$; qty $1:1$; $D<K_1-K_2$; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined debit.** A rally through $K_1$ loses $D$. A squeeze the other way still prints $-D$ at expiry. Time is not your friend the way it is on a credit put spread.
- **Capped downside gain.** A collapse through $K_2$ does not pay more than $P_{\max}$. A name that goes to zero after you sold a 10% OTM put still pays the width minus $D$, not $K_1$.
- **Assignment.** American short put at $K_2$ can be exercised early. You can be long stock you did not want, while still long the $K_1$ put.
- **Wide $D$.** A fat debit relative to width leaves almost no $P_{\max}$. Put skew makes this more common than on the call side: paying $\$4.50$ for a $\$5$ wide put spread is a thin lottery, not a conservative hedge.
- **Wrong signs.** Buying $K_2$ and selling $K_1$ is a bull put spread. You would then want the name to stay up. Tests on $L_{\max}=D$ with $P_{\max}$ at $S_T=0$ will catch the flip.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(K_1-S_T)_+-(K_2-S_T)_+-D$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T\ge K_1$, $f_T=-D=-L_{\max}$. For $S_T\le K_2$, $f_T=K_1-K_2-D=P_{\max}$.
- Reject a spec with $K_2\ge K_1$, unequal quantities, or $D\ge K_1-K_2$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
