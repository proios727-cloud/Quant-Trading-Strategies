---
rank: 23
slug: short-strangle
title: "Short Strangle"
asset_class: "options"
style: "short volatility / income"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 023. Short Strangle

| Field | Value |
|---|---|
| Popularity rank (this kit) | 23 of 101 |
| Why it sits here | More common than short straddles in retail and market-making income books because OTM wings reduce (but do not bound) risk. |
| Aliases | — |
| Asset class | options |
| Style | short volatility / income |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Short OTM call $K_1$ and short OTM put $K_2$. Lower credit and lower (still unlimited) risk versus a short straddle.

You are betting that $S_T$ finishes inside $[K_2,K_1]$ so both options die and you keep $C$. You are not running a defined-risk book: OTM wings delay the pain, they do not cap it. If the mandate forbids naked shorts, buy further wings and use the iron condor. You are also not harvesting a typical P&L of $C$; that is the best case on the whole interior plateau. The tails still fund the income.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the put is worth $K_2$ and $f_T=C-K_2$, a large loss. At $S_T=K_2$ you enter the plateau; through $K_1$, $f_T=C=P_{\max}$. Far above $K_1$ the call is worth $S_T-K_1$ and $f_T=C-(S_T-K_1)$, unbounded negative.

## 2. First principles

A short European call with OTM strike $K_1>S_0$ pays

$$
-(S_T - K_1)_+
$$

That is the right-hand hole, moved out from ATM. Below $K_1$ it is zero. Above $K_1$ it falls one-for-one without bound. Further OTM is less credit and a later start to the loss, not a cap.

A short European put with OTM strike $K_2<S_0$ pays

$$
-(K_2 - S_T)_+
$$

That is the left-hand hole, moved out from ATM. Above $K_2$ it is zero. Below $K_2$ it falls one-for-one. Same expiry is load-bearing. Asymmetric deltas leak direction.

Selling both brings in a credit $C$ at $t=0$, smaller than the ATM-straddle credit because both strikes are away from spot. Adding the three pieces is the short strangle:

$$
f_T = -(S_T - K_1)_+ - (K_2 - S_T)_+ + C
$$

$C$ is two OTM bids (or better). Inside $[K_2,K_1]$ both options die and you keep $C$. Outside that interval the loss tracks $S_T$ one-for-one and is not capped. You sold a cheaper strangle than a straddle; you did not buy a bound. The iron condor is this file plus long further wings.

That is the whole strategy. Everything below is how to pick the wings, when to replace them with an iron condor, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1$ | short OTM call strike, $K_1 > S_0$ |
| $K_2$ | short OTM put strike, $K_2 < S_0$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$.

## 4. Mathematics

### 4.1 Terminal payoff

Short OTM call plus short OTM put, net credit $C$:

$$
f_T = -(S_T - K_1)_+ - (K_2 - S_T)_+ + C
$$

Flat at $C$ on $[K_2,K_1]$, then linear down outside, no floor. Tests must keep both short signs. Sketch: $S_T=0$ prints $C-K_2$; through the interior prints $C$; far above $K_1$ prints $-\infty$.

### 4.2 Break-evens

On the call side, $C-(S_T-K_1)=0$ with $S_T>K_1$:

$$
S^\ast_{\mathrm{up}} = K_1 + C
$$

A rally must clear the short call and then eat $C$. The profitable band extends $C$ beyond each wing, which is why OTM shorts feel safer than ATM shorts until they do not. Beyond $S^\ast_{\mathrm{up}}$ the loss is uncapped.

On the put side, $C-(K_2-S_T)=0$ with $S_T<K_2$:

$$
S^\ast_{\mathrm{down}} = K_2 - C
$$

Symmetric on the left. A crash through $K_2$ by more than $C$ is a loss that can still run to $C-K_2$ at zero. That number is smaller than the short straddle's $C-K$ only because $K_2<K$, not because a bound exists.

### 4.3 Extrema

Maximum profit is the credit, attained for $S_T \in [K_2,K_1]$:

$$
P_{\max} = C
$$

The whole interior is the best case, not a single pin. That is why short strangles win more often than short straddles. The mean is still not $C$, because the tails are unbounded.

Maximum loss is unbounded in either direction:

$$
L_{\max} = \text{unlimited}
$$

OTM wings delay the pain; they do not cap it. Size off a stress $L$ at a gap, never off $C$. The defined-risk substitute is the iron condor in this kit.

## 5. Step-by-step algorithm

1. **Universe.** Only if the mandate allows naked short options. The defined-risk version is the iron condor: buy further OTM wings. This check exists so a "safer than a straddle" label does not smuggle unbounded tails into a defined-risk book.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places both wings OTM. A later print can put a wing ITM and look-ahead $C$.
3. **Strikes.** Sell call $K_1>S_0$ and put $K_2<S_0$. A common listed default is 16-delta wings. Further OTM is less $C$ and a wider plateau. Document delta versus moneyness on a skewed name.
4. **Expiry.** Same $T$. Short-dated weekly/monthly is the usual income tenor. Short-dated means more theta and more gamma if a wing is tested into expiry.
5. **Size.** One short call and one short put per lot. If you stay naked, size off $L$ at a stress move, not off credit. A 25% crash against a 16-delta put is still tens of dollars per share times $m$.
6. **Premium.** $C$ is the net credit actually received. OTM mids overstate $C$.
7. **Blotter.** Emit a two-legged short-strangle intent. Do not route live orders. One ticket keeps a wing from going on alone.
8. **Risk overlay.** Replace with an iron condor, or stop, if a wing is tested. That overlay is not part of expiry $f_T$. Without it, this file is hold-to-expiry with unlimited $L$.

## 6. Execution protocol

- Enter as a strangle (one ticket, net credit). Do not sell one wing without the other.
- Iron condor is the defined-risk version: buy further OTM wings.
- Pin risk at either strike into expiry. Assignment on American shorts.
- Cap lots by stress $L$ at a gap, not by $C$.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol (and delta if you select 16-delta wings)
- Multiplier $m$ (usually $100$ for US equity options)
- Margin parameters sufficient to refuse the ticket if naked shorts are not permitted
- Dividends and rates if you mark to a pricing model rather than to mid

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| wings | 16-delta | common listed default |
| $K_1>S_0>K_2$ | required | OTM call and OTM put |
| tenor | weekly / monthly | income cluster |
| quantity | $1:1$ | short call and short put |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_strangle` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag. `L_max` is unbounded.
5. `validate(spec)` — $K_1>K_2$; short call at $K_1$, short put at $K_2$; qty $1:1$; $P_{\max}=C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unlimited loss.** OTM wings delay the pain; they do not cap it. A crash through a 16-delta put on a $\$100$ name can still be $\$20$–$\$40$ per share against a $\$1$–$\$2$ credit, times $m$.
- **Pin.** Either short strike can pin into expiry. Assignment on the put prints long stock; assignment on the call prints short stock. The plateau identity assumes both options expire, not that one is exercised.
- **Margin expansion.** Same failure mode as the short straddle, slightly later. A tested wing still triggers variation margin as if you were short a near-ATM option.
- **Credit-sizing.** Sizing off $C$ rather than a stress $L$ is the usual blow-up. Ten lots because "it's only $\$1.50$ of credit" is ten times the gap.
- **Asymmetric wings.** A close put and a far call is a bullish credit package, not a neutral strangle. Delta leak is a directional bet you did not write down.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $-(S_T-K_1)_+-(K_2-S_T)_++C$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- For $S_T \in [K_2,K_1]$, $f_T=C=P_{\max}$. As $S_T\to\infty$ or $S_T\to 0$, $f_T\to-\infty$.
- Reject a spec with $K_1\le K_2$, a long option leg, or unequal quantities.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
