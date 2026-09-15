---
rank: 22
slug: long-strangle
title: "Long Strangle"
asset_class: "options"
style: "long volatility / cheaper than straddle"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 022. Long Strangle

| Field | Value |
|---|---|
| Popularity rank (this kit) | 22 of 101 |
| Why it sits here | Standard cheaper long-vol alternative to the straddle. Wide use in event trading. |
| Aliases | — |
| Asset class | options |
| Style | long volatility / cheaper than straddle |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long OTM call $K_1$ and long OTM put $K_2 < K_1$. Cheaper than a straddle; needs a larger move to break even.

You are betting that $\lvert S_T\rvert$ travels outside $[K_2,K_1]$ by more than $D$. Direction is still not the bet; the required move is larger than a straddle's. You are not buying an ATM V, and you are not selling vol. Cheap is not free: the dead zone is the whole interval between the wings, not a single strike. Implied-vol crush after a known event can still mark the package badly if you exit early.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the put is worth $K_2$ and $f_T=K_2-D$, a profit if $K_2>D$. At $S_T=K_2$ or anywhere through $K_1$ both options are at or out of the money and $f_T=-D=-L_{\max}$. Far above $K_1$ the call is worth $S_T-K_1$ and $f_T=S_T-K_1-D$, unbounded.

## 2. First principles

A long European call with OTM strike $K_1>S_0$ pays

$$
(S_T - K_1)_+
$$

That is the right-hand wing. It is zero until $S_T$ clears $K_1$, then rises one-for-one. Further OTM is cheaper and needs a bigger rally. This is not an ATM call; putting $K_1\approx S_0$ turns the package toward a straddle.

A long European put with OTM strike $K_2<S_0$ pays

$$
(K_2 - S_T)_+
$$

That is the left-hand wing. It is zero until $S_T$ breaks $K_2$, then rises one-for-one as $S_T$ falls. Same expiry as the call is load-bearing. Asymmetric deltas leave residual direction unless you flatten with stock.

Buying both costs a debit $D$ at $t=0$, smaller than the ATM-straddle debit because both strikes are away from spot. Adding the three pieces is the long strangle:

$$
f_T = (S_T - K_1)_+ + (K_2 - S_T)_+ - D
$$

$D$ is two OTM asks (or better), not two mids. Inside $(K_2,K_1)$ both options die and you lose $D$. You need $S_T$ outside that interval by more than $D$ to get paid. Direction is still not the bet; the required move is larger than a straddle’s. The shape is a U with a flat bottom, not a V.

That is the whole strategy. Everything below is how to pick the two strikes, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long OTM call strike, $K_1 > S_0$ |
| $K_2$ | long OTM put strike, $K_2 < S_0$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$.

## 4. Mathematics

### 4.1 Terminal payoff

Long OTM call plus long OTM put, net debit $D$:

$$
f_T = (S_T - K_1)_+ + (K_2 - S_T)_+ - D
$$

Flat at $-D$ on $[K_2,K_1]$, then linear outside. Tests must keep both kinks and both long signs. Sketch: $S_T=0$ prints $K_2-D$; through the interior prints $-D$; far above $K_1$ prints $S_T-K_1-D$.

### 4.2 Break-evens

On the call side, $(S_T-K_1)_+-D=0$ with $S_T>K_1$:

$$
S^\ast_{\mathrm{up}} = K_1 + D
$$

The name must clear the call strike by another $D$. A 16-delta call plus a $\$2$ debit on a $\$100$ name does not break even at the strike; it breaks even $\$2$ further out. That extra distance is why "cheap" strangles still lose on a typical event move.

On the put side, $(K_2-S_T)_+-D=0$ with $S_T<K_2$:

$$
S^\ast_{\mathrm{down}} = K_2 - D
$$

Same extra distance the other way. If $K_2-D\le 0$, a total wipe-out still profits. That is more plausible here than on a short-dated ATM straddle because $K_2$ is already OTM, but $D$ is also smaller.

### 4.3 Extrema

Maximum profit is unbounded in either direction:

$$
P_{\max} = \text{unlimited}
$$

A takeover or a bankruptcy both pay once they have cleared the extra OTM distance plus $D$. Expiry $P_{\max}$ is a bound; event traders often exit into the print.

Maximum loss is the debit, attained for $S_T \in [K_2,K_1]$:

$$
L_{\max} = D
$$

The whole interior is the max-loss plateau, not a single pin. A name that drifts 3% when your wings were 8% away still loses $D$. That is the usual strangle outcome, not a rare pin.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with OTM call and put wings. Open interest on both strikes above a minimum. A missing wing is a long call or a long put, not a strangle.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places both wings OTM. A later print can put one strike ITM and look-ahead $D$.
3. **Strikes.** Buy call $K_1>S_0$ and put $K_2<S_0$. Liquid defaults: 10-delta, 16-delta, or 25-delta wings. Further OTM is cheaper and a wider dead zone. Document delta versus moneyness; they are not the same strikes on a skewed name.
4. **Expiry.** Same $T$. Event-driven tenors match the long straddle (7–45 days typical). The event must sit inside both lives. Mixed expiries are a dual-expiry vol book, not this file.
5. **Size.** One call and one put per lot. If strikes are asymmetric, delta is not zero; flatten with stock only if the mandate is a pure vol bet. Residual delta is a directional leak, not a rounding error.
6. **Premium.** $D$ is the net debit actually paid. OTM wings have wide markets; mid is a poor $D$.
7. **Blotter.** Emit a two-legged strangle intent. Do not route live orders. One ticket avoids a one-legged long option.
8. **Hold.** Typical holding is into a known event, then exit. Expiry identities describe hold-to-$T$ P&L only. Early exit is a mark, including remaining time value on both wings.

## 6. Execution protocol

- Enter as a strangle (one ticket). Same as the straddle: do not lift both wings separately unless you can warehouse a one-legged long option.
- Implied vol paid is still the bet; the required realized move is larger than $D/S_0$ by the extra OTM distance.
- Cap lots by ADV on the tighter wing.
- If you delta-hedge, expiry identities no longer describe P&L.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol (and delta if you select by delta rather than by moneyness)
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg unless you flatten delta), book value, earnings as a signal.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| wings | 10-delta / 16-delta / 25-delta | liquid listed choices |
| $K_1>S_0>K_2$ | required | OTM call and OTM put |
| tenor | 7–45 days | event vol |
| quantity | $1:1$ | call qty = put qty |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_strangle` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $-D$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1>K_2$; long call at $K_1$, long put at $K_2$; qty $1:1$; $L_{\max}=D$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Larger required move** than a straddle. Cheap is not free: break-evens sit outside $K_1$ and $K_2$. A 5% earnings move on 10-delta wings that were 8% away still loses $D$.
- **Theta and IV crush.** Same as the long straddle; $L_{\max}=D$ only at expiry. Event strangles often expire or are sold into a crush even when the stock "moved."
- **Asymmetric strikes.** Residual delta is a directional leak unless flattened. A 10-delta call and a 25-delta put is a bearish package with a vol wrapper.
- **Dead zone.** $S_T \in [K_2,K_1]$ realizes $L_{\max}$. That interval can be 10–20% of spot. Most days finish there.
- **Wide OTM markets.** Paying the offer on both wings can make $D$ a large fraction of the distance to the nearest strike, which pushes $S^\ast$ out even further.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K_1)_++(K_2-S_T)_+-D$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T \in [K_2,K_1]$, $f_T=-D=-L_{\max}$.
- Reject a spec with $K_1\le K_2$, a short leg, or unequal quantities.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
