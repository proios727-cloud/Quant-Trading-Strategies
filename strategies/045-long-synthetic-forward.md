---
rank: 45
slug: long-synthetic-forward
title: "Long Synthetic Forward"
asset_class: "options"
style: "directional bullish / synthetic futures"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 045. Long Synthetic Forward

| Field | Value |
|---|---|
| Popularity rank (this kit) | 45 of 101 |
| Why it sits here | The put-call-parity construction of a long forward. Used when futures are unavailable or to arb vs listed forwards. |
| Aliases | synthetic long futures |
| Asset class | options |
| Style | directional bullish / synthetic futures |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long ATM call, short ATM put, $K = S_0$. Replicates a long forward with delivery price $K$. $|H| \ll S_0$.

You are betting that $S_T$ finishes above $K+H$, the same bet as a long forward or long stock. You are not long vol: the call and the put cancel into a linear claim. You are not running a conversion against shares unless you add a stock leg this file does not require. $|H|\ll S_0$ when $K=S_0$ and the chain is tight; a large $|H|$ is a stale quote or a wrong strike, not a feature. American early exercise breaks exact parity.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the short put is worth $K$ and $f_T=-(K+H)=-L_{\max}$. At $S_T=K$ both options are at the money and $f_T=-H$, a small debit or credit. Far above $K$ the call is worth $S_T-K$ and $f_T=S_T-K-H$, unbounded, slope $+1$ with no kink.

## 2. First principles

A long European call with strike $K$ pays

$$
(S_T - K)_+
$$

That is the right half of a forward. Below $K$ it is zero. Above $K$ it rises one-for-one. Alone it is a bullish debit with a kink. The synthetic forward exists to fill the left half with a short put so the kink disappears.

A short European put with the same strike pays

$$
-(K - S_T)_+
$$

That is the left half. Above $K$ it is zero. Below $K$ it falls one-for-one, which is exactly the forward's left tail. Same strike and same expiry are load-bearing: a mismatch leaves a vertical or a time spread, not a forward.

Net option premium is $H$: $H=D$ if the call costs more than the put brings in, $H=-C$ if the put credit exceeds the call debit. Adding the three pieces is the long synthetic forward:

$$
f_T = (S_T - K)_+ - (K - S_T)_+ - H
$$

$H$ is two ATM fills, not two mids. On a tight chain with $K=S_0$, $|H|$ should be small (carry and skew, not a vol premium). A fat $|H|$ means you are not synthesizing the forward you think you are.

The call–put identity $(S_T-K)_+-(K-S_T)_+=S_T-K$ collapses the options to a linear claim:

$$
f_T = S_T - K - H
$$

That is a long forward with delivery price $K$, shifted by the net premium. You are not long vol. You are long the underlying, synthetically, with $|H|\ll S_0$ when $K=S_0$ and the chain is tight. There is no kink once both legs are on. A one-legged fill (long call without the short put) restores the kink and is a different strategy.

That is the whole strategy. Everything below is how to match $K$ and expiry to the forward you are synthesizing, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | common ATM strike, typically $K=S_0$ |
| $H$ | net premium paid ($D$ if debit, $-C$ if credit) |
| $f_T$ | terminal P&L including $H$ |
| $S^\ast$ | expiry break-even, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Both legs share expiry $T$ and quantity $1:1$. No stock leg is required; the stock is synthesized.

## 4. Mathematics

### 4.1 Terminal payoff

Long call minus short put, net premium $H$:

$$
f_T = (S_T - K)_+ - (K - S_T)_+ - H = S_T - K - H
$$

The identity is linear in $S_T$. There is no kink in $f_T$ once both legs are on. Tests must match both writings to `1e-8`. Sketch: $S_T=0$ prints $-(K+H)$; at $K$ prints $-H$; far above prints $S_T-K-H$ with slope $1$.

### 4.2 Break-even

Set $S_T-K-H=0$:

$$
S^\ast = K + H
$$

A debit combo ($H>0$) needs the underlying to rally through $K$ by $H$. A credit combo ($H<0$) is already in the money at $K$. On a tight ATM chain, $S^\ast$ sits essentially at $K$. A large $H$ moves the effective delivery price and is a warning, not a feature.

### 4.3 Extrema

Maximum profit is unbounded as $S_T \to \infty$:

$$
P_{\max} = \text{unlimited}
$$

Same as long stock or a long future. The options did not cap the right tail. They synthesized it.

Maximum loss as $S_T \to 0$ is the delivery price plus net premium:

$$
L_{\max} = K + H
$$

A bankruptcy print loses about $K$, plus any net debit. That is forward risk, not option risk. Do not describe this file as defined-risk because it is built from options.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with a tight ATM chain, or a listed future you intend to synthesize. Open interest on both the call and the put above a minimum. A wide ATM market makes $|H|$ large and the synthetic a poor future.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K$. A later print look-aheads $H$ and the implied forward.
3. **Strike.** Choose $K=S_0$ (ATM), or the listed strike nearest the future’s delivery price. A far strike synthesizes a far forward, which is a different carry package.
4. **Expiry.** Match expiry to the futures you are synthesizing. A mismatched expiry is a calendar basis, not this forward.
5. **Size.** Buy $1$ ATM call, sell $1$ ATM put, same $K$ and expiry. Unequal quantities leave residual optionality. Extra puts are a ratio, not a forward.
6. **Premium.** Record $H$ from actual fills. $|H|\ll S_0$ on a tight ATM chain; a large $|H|$ is a stale quote or a wrong strike. That check is how you know the combo is actually a forward.
7. **Blotter.** Emit a conversion/reversal-style two-legged intent. Do not route live orders. One ticket keeps the short put from going on without the long call, or the reverse.
8. **Check.** Compare implied forward $K + H e^{rT}$ (European, rates) to listed futures. That is the conversion/reversal complex, adjacent to the long box. A gap is a basis trade, not a license to ignore dividends and rates.

## 6. Execution protocol

- Enter as a combo (one ticket). Do not buy the call without the short put, or you are long a naked call.
- American early exercise breaks exact parity. These identities are European-style claims.
- If you hold this versus a listed future, the residual is a basis trade, not a directional overlay. Carry rates and dividends explicitly in that case.
- Cap lots by ADV on the tighter of the two ATM options.

## 7. Data contract

Required, point-in-time, at $t=0$:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol
- Multiplier $m$ (usually $100$ for US equity options)
- Dividends and rates (needed to compare $K+H e^{rT}$ to listed forwards/futures)

At expiry or at exit: underlying print used for settlement, and any early-exercise events for American options. These identities are European-style claims; American early exercise can invalidate them.

Not used by this spec: stock borrow (no stock leg unless you convert against shares), book value, earnings.

No restatement peeking.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $K$ | $S_0$ ATM | or the future’s delivery strike |
| tenor | match the future | same expiry as the contract you synthesize |
| quantity | $1:1$ | long call, short put |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_synthetic_forward` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Equals $-H$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file, including the collapsed form $s_t-K-H$.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — same $K$ and expiry; long call, short put; qty $1:1$; $f_T=s_t-K-H$ on a dense $S_T$ grid to `1e-8`.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Forward risk.** Same as long stock/forward: unlimited upside, large downside $L_{\max}=K+H$. A 40% decline on a $\$100$ synthetic is about $\$40$ plus $H$, times $m$. The options did not define that risk away.
- **American early exercise** breaks exact parity. A short ATM put assigned overnight leaves you long stock against a long call — a conversion you may or may not have wanted, with a different financing clock.
- **Wide $H$.** A fat net debit is not a forward; it is a mis-struck or stale combo. Paying $\$4$ net on a $\$100$ ATM pair is a $\$4$ drag on delivery, not "a little carry."
- **One-legged fill.** A long call without the short put is a different strategy. The linear identity is gone until the put is on. The live book is then long gamma, not long a forward.
- **Dividend / rate miss.** Comparing $K+H$ to a listed future without $e^{rT}$ and dividends calls a carry gap an arbitrage. That gap is often the box.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(S_T-K)_+-(K-S_T)_+-H$ and also $S_T-K-H$.
- Break-even: $f_T(S^\ast)=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=0$, $f_T=-(K+H)=-L_{\max}$. The map $S_T \mapsto f_T$ is affine with slope $1$.
- Reject a spec with unequal strikes, a long put, a short call, or unequal quantities.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant (through $H$) and does not create a kink.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
