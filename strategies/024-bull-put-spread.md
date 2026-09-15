---
rank: 24
slug: bull-put-spread
title: "Bull Put Spread"
asset_class: "options"
style: "bullish income / credit vertical"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 024. Bull Put Spread

| Field | Value |
|---|---|
| Popularity rank (this kit) | 24 of 101 |
| Why it sits here | The credit-vertical way to be mildly bullish. Extremely common in short-vol retail and market-making books. |
| Aliases | — |
| Asset class | options |
| Style | bullish income / credit vertical |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long OTM put $K_1$, short higher-strike OTM put $K_2 > K_1$. Net credit. Income if the stock stays above $K_2$.

You are betting that $S_T$ finishes at or above $K_2$ so both puts die and you keep $C$. You sold a put and bought a further-OTM put so the loss cannot exceed the width. You are not running a naked short put, and you are not buying a bearish debit vertical. Tiny $C$ versus width is a bad payoff, not a safer one. This vertical is often the put side of a credit iron condor.

Payoff sketch, one lot, ignore financing: at $S_T=0$ both puts are in the money and $f_T=C-(K_2-K_1)=-L_{\max}$. At $S_T=K_1$ you are at the bottom of the slope, still $-L_{\max}$. At $S_T=K_2$ the short put is at the money and $f_T=C=P_{\max}$. Far above $K_2$ both puts are dead and $f_T$ stays $C$.

## 2. First principles

A long European put with the lower strike $K_1$ pays

$$
(K_1 - S_T)_+
$$

That is the wing. Below $K_1$ it pays $K_1-S_T$. Above $K_1$ it is zero. You buy it so a crash cannot take more than the width on this vertical. Without it this file is a naked short put.

A short European put with the higher strike $K_2>K_1$ pays

$$
-(K_2 - S_T)_+
$$

That is the income engine. Below $K_2$ it costs $K_2-S_T$. Above $K_2$ it is zero. The short put is closer to the money, so it is worth more than the wing. That gap is $C$.

The short put is closer to the money, so it brings in more premium than the long put costs. The package is a net credit $C$ at $t=0$. Adding the three pieces is the bull put spread:

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ + C
$$

$C$ must be less than $K_2-K_1$ or there is no room for a positive $P_{\max}$ after a complete width loss. $C$ is two fills, not two mids. Above $K_2$ both puts die and you keep $C$. Between $K_1$ and $K_2$ the short put is in the money and the long is not, so P&L falls as $S_T$ falls. Below $K_1$ both puts are in the money and the loss is the width $K_2-K_1$ minus $C$. You sold a put and bought a further-OTM put so the loss cannot exceed that width.

That is the whole strategy. Everything below is how to pick the two strikes, how to keep $C < K_2-K_1$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long OTM put strike |
| $K_2$ | short OTM put strike, $K_2 > K_1$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$. Typically both strikes are OTM, $K_2 < S_0$. Structure so $C < K_2-K_1$.

## 4. Mathematics

### 4.1 Terminal payoff

Long put $K_1$ minus short put $K_2$, net credit $C$:

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ + C
$$

Credit, not debit. Tests must keep the signs: long the low strike, short the high strike. The opposite signs are a bear put spread. Sketch: $S_T=0$ prints $-L_{\max}$; at $K_2$ and far above, $P_{\max}=C$.

### 4.2 Break-even

Set $f_T=0$ on $K_1 < S_T < K_2$, where $f_T = C - (K_2-S_T)$:

$$
S^\ast = K_2 - C
$$

A decline of $C$ through the short strike eats the credit. Below $S^\ast$ you lose until the long put at $K_1$ stops the bleed. If $C$ is small relative to width, most of the wing is a losing region.

### 4.3 Extrema

Maximum profit is the credit, attained for $S_T \ge K_2$:

$$
P_{\max} = C
$$

Sitting still above the short strike is the designed outcome. Time is on your side the way it is not on a debit put spread. Mark-to-market can still be negative on that path if implied vol rises.

Maximum loss is the width net of the credit, attained for $S_T \le K_1$:

$$
L_{\max} = K_2 - K_1 - C
$$

A complete test of the wing realizes this number. For a $\$5$ wide put spread and a $\$1$ credit, $L_{\max}=\$4$ per share, times $m$. Defined is not small. Sizing off $C$ rather than $L_{\max}$ is the usual mistake.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with two tight put strikes. Open interest on both legs above a minimum. A missing long wing is a naked short put. Wide put markets shrink $C$ and can make $C$ fail the width check.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. Default structure wants $K_2<S_0$. A later print can put the short strike ITM and look-ahead $C$.
3. **Strikes.** Sell put $K_2$, buy put $K_1<K_2$, both OTM. Short strike typically 16–30 delta. Width 1–5% of spot. Closer shorts collect more $C$ and get tested more. Width is $L_{\max}+C$.
4. **Expiry.** Same $T$. Typical 1 week to 3 months. Mixed expiries are a diagonal, not this vertical. Short-dated credit puts harvest theta and take assignment risk into expiry.
5. **Size.** One short put and one long put per lot. Extra shorts without extra longs are a ratio spread with a different $L_{\max}$.
6. **Premium.** $C$ is the net credit actually received. Reject if $C \ge K_2-K_1$. That reject is a fill check. A credit as large as the width is not a listed bargain; it is a mis-struck ticket.
7. **Blotter.** Emit a two-legged net-credit vertical. Do not route live orders. One ticket keeps the short from going on without the wing.
8. **Hold.** Defined risk. Often the put side of an iron condor. Early management at 50% of credit is an overlay, not part of $f_T$.

## 6. Execution protocol

- Enter as a net-credit vertical (one ticket). Do not sell $K_2$ without $K_1$ already on.
- Pair with a bear call spread to form a long (credit) iron condor.
- American short-put assignment if $K_2$ is ITM.
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
| short strike $K_2$ | 16–30 delta | OTM put |
| width $K_2-K_1$ | 1–5% of spot | listed strikes |
| tenor | 1 week to 3 months | income cluster |
| quantity | $1:1$ | long $K_1$, short $K_2$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.bull_put_spread` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_2>K_1$; qty $1:1$; $C<K_2-K_1$; $P_{\max}=C$ and $L_{\max}=K_2-K_1-C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined gap.** A print through both strikes loses $L_{\max}$. A 12% overnight drop against a 5% wide, 16-delta short put still takes the whole width minus $C$, times $m$.
- **Assignment.** The short put at $K_2$ can be exercised early. You wake up long stock, still long the $K_1$ put, which is a conversion you did not ask for.
- **Credit too small.** Tiny $C$ versus width is a bad payoff, not a safer one. Collecting $\$0.15$ on a $\$5$ wing is a lottery you sold for almost nothing.
- **Wrong sign.** Buying $K_2$ and selling $K_1$ is a bear put spread, not this file. You would then need the name to fall. Tests on $P_{\max}=C$ at high $S_T$ will catch the flip.
- **Skew.** Put credit is richer than the matching call credit on many indexes, which is why this vertical is popular — and why the short strike gets tested in a crash more painfully than a call credit of the same delta.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(K_1-S_T)_+-(K_2-S_T)_++C$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T\ge K_2$, $f_T=C=P_{\max}$. For $S_T\le K_1$, $f_T=C-(K_2-K_1)=-L_{\max}$.
- Reject a spec with $K_2\le K_1$, unequal quantities, or $C\ge K_2-K_1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
