---
rank: 65
slug: short-synthetic-forward
title: "Short Synthetic Forward"
asset_class: "options"
style: "directional bearish / synthetic short futures"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 065. Short Synthetic Forward

| Field | Value |
|---|---|
| Popularity rank (this kit) | 65 of 101 |
| Why it sits here | Put-call-parity short forward. Standard conversion/reversal building block. |
| Aliases | — |
| Asset class | options |
| Style | directional bearish / synthetic short futures |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long one ATM put and short one ATM call, same strike $K$ and same expiry $T$, typically $K = S_0$. The package replicates a short forward with delivery price $K$. Use it to get short exposure when stock borrow is expensive, or to reverse against listed futures.

You are betting that the underlying finishes below the implied delivery price. You are not betting that implied vol is high or low, and you are not betting that the smile is steep. Both options share $K$ and $T$, so the piecewise-linear kinks cancel and what remains is a line with slope $-1$. Gamma and vega of the two legs offset at inception when the chain is tight and both strikes are ATM.

The typical user is a conversion/reversal desk, or anyone who wants a listed short without locating shares. Horizon is the option expiry you chose: hold to $T$, or unwind early against a listed future if the implied forward cheapens. If you cannot get a two-sided ATM market, this is not the trade — a wide $H$ is a stale combo, not a forward.

A one-legged fill is a different book. A long put without the short call is a crash hedge. A short call without the long put is an uncovered rally. Size off the unhedged upside, not off the small net premium.

## 2. First principles

A European call and put with the same $K$ and $T$ are piecewise linear. The long put pays the positive part of $K - S_T$:

$$
(K - S_T)_+
$$

That is the usual put intrinsic at expiry: $K-S_T$ if spot finishes below the strike, otherwise zero. It is the crash side of the synthetic. Skip this piece and you no longer have a short forward; you have a naked short call.

The short call pays the negative of the positive part of $S_T - K$:

$$
-(S_T - K)_+
$$

That is the rally side. Above $K$ the call is in the money and you owe $S_T-K$. Below $K$ the call expires worthless and this term is zero. Together with the put, the two kinks are supposed to cancel.

Subtract the net premium paid $H$. The listed-leg P&L is therefore

$$
f_T = (K - S_T)_+ - (S_T - K)_+ - H
$$

$H$ is cash at $t=0$: pay the put ask, receive the call bid, plus fees. A debit ($H>0$) means you paid to put the short forward on; a credit ($H<0$) means the market paid you. Either way, $H$ is a parallel shift of the line, not a change of slope. If you omit $H$ from P&L, the break-even and the max-profit identity are both wrong.

On $S_T \ge K$ the put is worthless and the short call is in the money, so the option package equals $K - S_T$. On $S_T < K$ the call is worthless and the long put is in the money, so the package again equals $K - S_T$. The two positive parts therefore cancel to a short forward:

$$
(K - S_T)_+ - (S_T - K)_+ = K - S_T
$$

This is put-call cancellation, not an approximation. It holds pathwise at expiry for European options with a common strike and expiry. American early exercise, a mismatched strike, or a one-legged fill all break it. If a unit test does not recover $K-S_T$ on a dense $S_T$ grid, the legs are wrong.

Terminal P&L is the short-forward identity shifted by premium:

$$
f_T = K - S_T - H
$$

Slope $-1$ in $S_T$. Profit if spot falls, loss if it rallies, shifted by whatever you paid or received up front. There is no kink left in $f_T$. That is why this file is a directional overlay, not a vol sale.

**Payoff sketch.** Take $K=100$ and a tiny debit $H=1$. At $S_T=0$ you keep almost the strike: $f_T=99$. At $S_T=K=100$ you lose the debit: $f_T=-1$. Far above, say $S_T=200$, the short call is deep in the money and $f_T=-101$. The sketch is a straight line through those three points. Unlimited loss is the rally, not the crash.

That is the whole strategy. You are not trading volatility. You are synthesizing a short futures position from a 1:1 put-call pair.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K$ | common strike of the long put and short call |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | terminal P&L including initial premium |
| $S^\ast$ | expiry break-even where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry, ignoring financing and fees |

One long put and one short call. Same expiry. Default $K = S_0$ (ATM).

## 4. Mathematics

### 4.1 Premium

Quotes define $H$ at $t=0$: pay the put ask, receive the call bid, plus fees. $|H| \ll S_0$ when both strikes are ATM and the book is tight. A fat $|H|$ is a warning, not a feature: stale quotes, a wrong strike, or a one-sided market. Record $H$ from actual fills, not from a mid that was never tradable.

### 4.2 Terminal payoff

From the listed legs:

$$
f_T = (K - S_T)_+ - (S_T - K)_+ - H
$$

This is the implementation identity: sum the two option settlements and subtract cash paid. Use it in tests even after you collapse to the linear form, so a sign error on either leg cannot hide.

After the put-call cancellation:

$$
f_T = K - S_T - H
$$

Same number, simpler closed form. Metrics, break-evens, and $P_{\max}$ are all read from this line. If the two expressions disagree on a grid, stop: the code does not match this spec.

### 4.3 Break-even

Set $f_T = 0$:

$$
S^\ast = K - H
$$

A small debit ($H>0$) moves the break-even below $K$. A small credit ($H<0$) moves it above $K$. You need spot to finish below $S^\ast$, not merely below $K$, if you paid to enter. Fees that inflate $H$ move $S^\ast$ the same way. There is only one break-even because the payoff is a line.

### 4.4 Max profit and loss

If $S_T \to 0$, P&L approaches $K - H$:

$$
P_{\max} = K - H
$$

Stock cannot go below zero, so the short-forward profit is capped at roughly the strike. That is the crash case, and it is the *best* case for this book. Do not report unlimited profit.

A rally has no cap on the short call:

$$
L_{\max} = \text{unlimited}
$$

There is no wing above $K$. A melt-up is an uncovered short call. Size, stops, and ADV caps have to live on this tail, not on $|H|$.

### 4.5 Mark-to-market

Before expiry, mark is the sum of option mids minus initial $H$. The $P_{\max}$ / $L_{\max}$ identities are **expiry** quantities. If you delta-hedge, those identities no longer describe P&L; carry $\Delta, \Gamma, \Theta, \nu$ separately. Options pay premium up front, so $H$ already capitalizes the cash; still accrue interest on the cash balance. A mid-to-mid mark that ignores assignment and borrow is not the same as holding a locatable short stock.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed equity or index options. Same underlying on both legs. Open interest and bid-ask tight enough that $|H|$ is a small fraction of $S_0$. This step exists so you do not synthesize a forward out of a wide, one-sided chain; the identity is exact, the fill is not.
2. **Strike and expiry.** Choose ATM $K \approx S_0$ and a single expiry $T$ matching the forward you want to synthesize. A mismatched $T$ is a different forward; a mismatched $K$ is a different delivery price.
3. **Legs.** Buy 1 put $K$, sell 1 call $K$, same $T$. Quantity ratio $1:1$. Any other ratio is a risk reversal or a ratio spread, not this file.
4. **Premium.** Compute $H$ from live bid/ask (pay put, receive call). Reject if $|H|$ is large versus the listed-futures basis you are targeting. A large $|H|$ means you are not at the futures you think you are.
5. **Metrics.** Store $S^\ast = K - H$, $P_{\max} = K - H$, and $L_{\max}$ unlimited. These are the numbers a blotter and a risk limit need before any order intent is emitted.
6. **Blotter.** Emit a two-leg intent (or a reversal/conversion ticket). Round to the option multiplier. Do not route live orders. The ticket is research output, not a live send.
7. **Hold.** Hold to $T$, or unwind against listed futures if the implied forward cheapens. American early exercise on either leg breaks the exact identity; flatten if assigned. The hold step exists because the linear $f_T$ is an *expiry* claim.

## 6. Execution protocol

- Default fill: a single reversal-style ticket (long put, short call) at a net-premium limit. Do not leg in unless you can warehouse one side. Legging the short call first is an uncovered sale.
- Use this to short when stock borrow is expensive, or to reverse versus listed futures. Compare implied forward $K - H e^{rT}$ (European, rates) to the futures print. If you skip the futures (or borrow) comparison, you cannot tell a cheap synthetic from a fair one.
- Cap size by option ADV and by the unhedged rally tail, not by $|H|$. Treating a $0.20$ debit as “small risk” is how the backtest lies.
- If the short call is American and goes ITM into an ex-dividend, assignment risk is the conversion/reversal residual, not a “free” stock short.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain: bid/ask, strike, expiry, call/put flag, open interest, implied vol, multiplier (usually 100 for US equity options)
- Dividends and rates if you mark to a model or compare to listed futures
- Listed futures (or stock borrow quotes) if the trade is a reversal versus those markets
- At expiry: settlement print, and any early-exercise events for American options

Not used by this spec: book value, earnings, SUE, a second expiry.

These identities are European-style claims. American early exercise can invalidate them. A delay-0 mid for $H$ is research-only; delay-1 fill is the default so the backtest does not trade the quote that determined the signal.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| strike | ATM, $K = S_0$ | same $K$ on put and call |
| quantity ratio | $1:1$ | one long put, one short call |
| expiry | match the target forward | typically 1 week to 3 months |
| $H$ | market | small vs $S_0$ if the book is tight |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.short_synthetic_forward` with:

1. `legs(spec) -> list[Leg]` — one long put and one short call, same $K$ and $T$, qty $1:1$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive); $H$ is the negative of that credit.
3. `payoff(s_t, spec) -> float` — implements $f_T = K - S_T - H$, equal to the listed-leg sum.
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — same strike and expiry, quantity ratio $1:1$, and $P_{\max}=K-H$ on a dense $S_T$ grid including $0$.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Rally.** The short call is uncovered. Loss is unlimited. A gap through $K$ on earnings or a buyout is the concrete path, not a slow grind you can “manage.”
- **Early exercise.** American assignment on the short call (dividends) or exercise of the long put breaks $f_T = K - S_T - H$. After assignment you may be short stock without the rebate you thought you had.
- **Pin.** Settlement exactly at $K$ can leave a residual stock position after one-sided exercise. The linear identity assumes both legs settle cleanly.
- **Financing.** The synthetic short does not automatically earn the stock-loan rebate of a locatable short. Marking P&L as if you were short shares overstates carry.
- **Wide $H$.** Using mid instead of bid/ask makes a fair combo look cheap. The backtest then “harvests” a spread that never filled.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $(K-S_T)_+ - (S_T-K)_+ - H$ and also equals $K - S_T - H$.
- At $S_T = 0$, $f_T = K - H = P_{\max}$.
- $f_T(S^\ast) = 0$ within $10^{-8}$ relative to $S_0$.
- Reject a spec with mismatched strikes, mismatched expiries, or quantity ratio other than $1:1$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and moves $S^\ast$ only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
