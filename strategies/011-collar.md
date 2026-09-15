---
rank: 11
slug: collar
title: "Collar"
asset_class: "options"
style: "hedge / moderately bullish"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 011. Collar

| Field | Value |
|---|---|
| Popularity rank (this kit) | 11 of 101 |
| Why it sits here | The institutional hedge around concentrated stock (executives, index overlays). Also called a fence. |
| Aliases | fence |
| Asset class | options |
| Style | hedge / moderately bullish |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long stock, long OTM put $K_1$, short OTM call $K_2 > K_1$. Covered call plus protective put. Moderately bullish, capital-gain with a floor and a cap.

You are betting that the stock stays between $K_1$ and $K_2$, or that a modest rally toward $K_2$ is enough. You want a floor under a concentrated long, and you are willing to sell the upside to pay for it. You are not running a free-standing short-vol book, and you are not buying unlimited upside. The usual institutional target is $H \approx 0$ (zero-cost collar): the short call finances the long put. You are also not buying a zero-loss guarantee: a gap through $K_1$ still loses $L_{\max}$.

Payoff sketch, one share, ignore financing: at $S_T=0$ the put pays $K_1$, the call dies, and $f_T=K_1-S_0-H=-L_{\max}$. At $S_T=K_1$ you are on the floor. Between $K_1$ and $K_2$ you own the stock, shifted by $H$. At $K_2$ and far above, the call caps you at $f_T=K_2-S_0-H=P_{\max}$.

## 2. First principles

A long share, marked from $S_0$, has terminal P&L

$$
S_T - S_0
$$

Unbounded both ways. The collar exists to cut both tails: buy a floor, sell a cap. The stock identity stays; the two options do the cutting.

A long put at $K_1$ pays the floor

$$
(K_1 - S_T)_+
$$

Below $K_1$ this rises one-for-one as $S_T$ falls, cancelling further stock loss. Above $K_1$ it is zero. That is the protective-put piece. Skew usually makes this wing expensive relative to the call you will sell.

A short call at $K_2>K_1$ pays the cap

$$
-(S_T - K_2)_+
$$

Above $K_2$ this falls one-for-one, cancelling further stock gain. Below $K_2$ it is zero. That is the covered-call piece. The short call is what finances the put when you target $H\approx 0$.

Net option premium is $H$: $H=D$ on a net-debit collar and $H=-C$ on a net-credit collar. Adding the four pieces is the collar:

$$
f_T = S_T - S_0 + (K_1 - S_T)_+ - (S_T - K_2)_+ - H
$$

$H>0$ means you paid for extra insurance (put richer than the call). $H<0$ means you sold more upside than you bought floor. $H=0$ is the zero-cost fence. Between $K_1$ and $K_2$ both options die and you own the stock, shifted by $H$. Below $K_1$ the put stops the loss. Above $K_2$ the call sells the stock away. The usual institutional target is $H \approx 0$ (zero-cost collar): the short call finances the long put.

That is the whole strategy. Everything below is just how to pick $K_1$ and $K_2$, how to hit $H\approx 0$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying purchase price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | long-put strike, $K_1 < S_0$ |
| $K_2$ | short-call strike, $K_2 > S_0$ |
| $H$ | net premium paid ($D$ if debit, $-C$ if credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $Q$ | share count (positive = long) |
| $m$ | option multiplier (usually $100$) |

One put and one call cover $m$ shares. Lot integrity is $Q = n m$ for integer $n \ge 1$.

## 4. Mathematics

### 4.1 Terminal payoff

Stock plus long put plus short call, net premium $H$:

$$
f_T = S_T - S_0 + (K_1 - S_T)_+ - (S_T - K_2)_+ - H
$$

Three pieces in $S_T$: a floor, a stock slope, a cap. Tests must keep both kinks. Sketch: $S_T=0$ prints $-L_{\max}$; at $K_1$ still the floor; between the strikes the stock line shifted by $H$; at $K_2$ and far above, $P_{\max}$.

For $S_T \le K_1$, $f_T = K_1 - S_0 - H$. For $K_1 \le S_T \le K_2$, $f_T = S_T - S_0 - H$. For $S_T \ge K_2$, $f_T = K_2 - S_0 - H$.

### 4.2 Break-even

Set $f_T=0$ on the interior $K_1 < S_T < K_2$:

$$
S^\ast = S_0 + H
$$

A debit collar ($H>0$) needs the stock to rally $H$ just to get back to flat. A credit collar ($H<0$) is already in the money at $S_0$ and breaks even slightly below the purchase price. A zero-cost collar ($H=0$) breaks even at $S_0$.

A zero-cost collar ($H=0$) breaks even at $S_0$.

### 4.3 Extrema

Maximum profit is the capped upside at $K_2$ net of $H$:

$$
P_{\max} = K_2 - S_0 - H
$$

A rally through $K_2$ does not pay more. Selling a closer call (smaller $K_2$) finances a cheaper put and shrinks $P_{\max}$. That is the fence's tradeoff, not a tracking error.

Maximum loss is the floor at $K_1$ plus $H$:

$$
L_{\max} = S_0 - K_1 + H
$$

A gap through $K_1$ still loses the deductible plus any net debit. A zero-cost collar with 10% OTM put and 10% OTM call has $L_{\max}=0.10 S_0$ and $P_{\max}=0.10 S_0$ when $H=0$. Skew usually forces a closer call or a debit to keep that put.

## 5. Step-by-step algorithm

1. **Universe.** Concentrated long stock (or an index overlay) with liquid OTM puts and calls. ADV above a minimum. Keep delisted names until the delist date. Illiquid wings make a zero-cost solve a mid fiction. Survivorship would drop the names that hit the floor.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ is the purchase mark and the moneyness of both strikes. A later print look-aheads $H$ and the zero-cost solve.
3. **Put strike.** Choose $K_1 < S_0$, typically 5–15% OTM. Lower $K_1$ is a cheaper put and a worse floor. This is the deductible. Executives often have a compliance band that pins $K_1$.
4. **Call strike.** Choose $K_2 > S_0$, typically 5–15% OTM. For a zero-cost collar, solve for $K_2$ given $K_1$ so that mid premia net to $H \approx 0$. Skew usually forces $K_2$ closer than $K_1$ is far. Document whether you solved on mids or on live bids/asks.
5. **Expiry.** Same $T$ on both options, tenor 1–12 months. Mixed expiries are a diagonal collar, not this payoff. Match the hedge window: a put that dies before the lock-up is not a lock-up hedge.
6. **Size.** Buy (or hold) $Q$ shares. Buy $Q/m$ puts. Sell $Q/m$ calls. Extra short calls are naked. Extra puts are a crash lottery. Lot integrity keeps assignment a round stock lot.
7. **Premium.** Record $H$ from actual fills, not mids. $H>0$ is a debit collar; $H<0$ is a credit collar. The zero-cost target is a solve, then a fill; the fill will not be exactly zero.
8. **Blotter.** Emit a three-way intent. Do not route live orders. One ticket keeps the stock overlay and both options together.

## 6. Execution protocol

- Often done as a three-way. Zero-cost collars: solve for $K_2$ given $K_1$ so that mid premia net to zero, then execute with a small debit tolerance.
- Prefer selling the call at the bid or better; buy the put between mid and ask unless the hedge is urgent.
- Dividend assignment on the short call is the same failure mode as a covered call.
- Cap $Q$ by ADV.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates if you mark to a pricing model rather than to mid, and if you solve a zero-cost $K_2$

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: borrow (the stock leg is long), book value, earnings.

No restatement peeking. Delisted names stay in the sample until the delist date.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| put OTM | 5–15% | $K_1/S_0 \in [0.85, 0.95]$ typical |
| call OTM | 5–15% | $K_2/S_0 \in [1.05, 1.15]$ typical |
| $H$ | $\approx 0$ | zero-cost is the usual institutional target |
| tenor | 1–12 months | match the hedge window |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.collar` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Equals $-H$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1<S_0<K_2$; $Q$ a multiple of $m$; put qty = call qty = $Q/m$; $P_{\max}$ / $L_{\max}$ match closed-form identities on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Sold upside.** A rally through $K_2$ assigns the stock away. A concentrated name that doubles after a 10% OTM collar still pays $P_{\max}$, not the double. That is often the complaint after a lock-up expires into a squeeze.
- **Floor, not zero.** A gap below $K_1$ still loses $L_{\max}$. A 15% OTM put on a name that halves overnight still loses the 15% deductible plus $H$.
- **Dividend assignment.** The short call can be exercised early into an ex-date. You lose the stock before the dividend and may be left long a put you no longer need.
- **Costly collar.** If you refuse to sell enough call premium, $H$ is a large debit and the floor is expensive. A "zero-cost" solve that is then filled $2$ wide on each wing is a debit collar by another name.
- **Compliance vs economics.** A mandated $K_1$ band can force a close $K_2$ on a skewed name. The fence still works; $P_{\max}$ just becomes very small.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $S_T-S_0+(K_1-S_T)_+-(S_T-K_2)_+-H$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K_2$, $f_T=P_{\max}$. At $S_T=K_1$ (and below), $f_T=-L_{\max}$.
- Zero-cost: $H=0$ implies $S^\ast=S_0$, $P_{\max}=K_2-S_0$, $L_{\max}=S_0-K_1$.
- Reject a spec with $K_1 \ge K_2$, missing stock, or option qty not equal to $Q/m$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
