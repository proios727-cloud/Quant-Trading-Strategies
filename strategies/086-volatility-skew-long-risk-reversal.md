---
rank: 86
slug: volatility-skew-long-risk-reversal
title: "Volatility Skew — Long Risk Reversal"
asset_class: "options"
style: "skew / directional"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 086. Volatility Skew — Long Risk Reversal

| Field | Value |
|---|---|
| Popularity rank (this kit) | 86 of 101 |
| Why it sits here | The listed-equity way to harvest put-over-call skew. Same legs as the long combo; the thesis is the skew, not a spot view, unless unhedged. |
| Aliases | long 25-delta risk reversal |
| Asset class | options |
| Style | skew / directional |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

OTM puts with $S_0 = K+\kappa$ tend to be priced richer than OTM calls with $S_0 = K-\kappa$. Long the OTM call and short the OTM put captures that skew. The listed legs are the same as the long combo (`073`). Unhedged, the book is still a directional crash-short. Delta-hedged, P&L tracks the 25-delta risk-reversal mark rather than expiry $f_T$.

You are betting that put-over-call richness is too high (hedged) or that you are willing to be long a combo that is often a credit (unhedged). You are not running market-neutral vol without a hedge. You are not running a different payoff from `073` on the option legs. The hedge flag and the thesis are what differ. Never treat an unhedged risk reversal as “market-neutral vol.”

The typical user is a skew book on index or liquid single-name options, at quoted 1m or 3m 25-delta (or 16-delta) RR points. Size off $L_{\max}=K_2+H$ when unhedged, and off jump/gap risk when hedged. Reject if the smile does not show put-over-call richness unless the spec is explicitly directional. Rebalance delta on a schedule; never skip a crash print.

## 2. First principles

Same two listed legs as the long combo: long OTM call $K_1$, short OTM put $K_2 < K_1$, same expiry, quantity $1:1$. Terminal P&L from those legs is

$$
f_T = (S_T - K_1)_+ - (K_2 - S_T)_+ - H
$$

Unhedged, this *is* `073`. The dead zone, unlimited call upside, and crash at $K_2$ are unchanged. $H$ is where skew shows up in cash: puts rich $\Rightarrow$ credit more often. If you change the payoff function because “this file is about vol,” you have broken the listed identity. Hedged P&L is a *different* function and must not overwrite this one.

The skew thesis is about $H$ and about implied vol, not about a different payoff. Let $\sigma_{\mathrm{put}}$ be implied vol at the OTM put and $\sigma_{\mathrm{call}}$ at the OTM call. Equity index books usually have

$$
\sigma_{\mathrm{put}} > \sigma_{\mathrm{call}}
$$

for roughly symmetric wings (25-delta or 16-delta). Then the put you sell is rich versus the call you buy, so $H$ is often a credit. Write that credit as put premium minus call premium. The inequality is a smile fact, not a guarantee that expiry $f_T$ is positive. Sticky-strike versus sticky-delta can move the RR mark even if this inequality still holds. If the smile is inverted (calls richer), a long RR is a directional debit unless you have a separate view.

A drop through the put strike still loses: at $S_T=0$,

$$
L_{\max} = K_2 + H
$$

Same crash identity as `073`. A skew credit ($H<0$) trims the hole slightly; it does not remove the short put. Hedging with stock or futures changes P&L *paths* but does not kill a gap through $K_2$. Size unhedged books off this number.

If unhedged, you are running `073`. If you delta-hedge with stock or futures, expiry identities no longer describe P&L. The working mark is then the change in the quoted 25-delta risk-reversal (call vol minus put vol, or the reverse sign convention of the desk), plus hedge P&L, plus residual jump risk.

**Payoff sketch (unhedged).** Same as `073`: at $S_T=0$, $f_T=-(K_2+H)$; in the dead zone, $f_T=-H$ (often a kept credit); far above $K_1$, unlimited. Hedged, throw this sketch away for P&L: you mark the RR and the hedge, and a jump still looks like a short put gap. Do not plot expiry $f_T$ as the hedged book’s result.

That is the whole strategy. Never treat an unhedged risk reversal as market-neutral vol.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_2 < K_1$ | short OTM put strike, long OTM call strike |
| $\kappa$ | wing gap used to talk about symmetric OTM strikes |
| $\sigma_{\mathrm{put}}$, $\sigma_{\mathrm{call}}$ | implied vols of the two wings |
| $(x)_+$ | $\max(x,0)$ |
| $H$ | net premium paid ($D$ on a debit, $-C$ on a credit) |
| $f_T$ | unhedged terminal P&L including $H$ |
| $S^\ast$ | unhedged expiry break-even where $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | unhedged maximum profit and loss at expiry |

25-delta call long, 25-delta put short, same expiry. Optional stock/futures hedge.

## 4. Mathematics

### 4.1 Premium and skew

$H$ is the listed net premium of long $K_1$ call minus short $K_2$ put. When puts are richer, $H<0$ (credit). That credit is the skew harvest **only if** spot does not crash through $K_2$. Record the RR mark $\sigma_{\mathrm{call}}-\sigma_{\mathrm{put}}$ (or the desk’s sign) alongside $H$. A credit with a smile that does not show put-over-call richness is a quote artifact, not a thesis.

### 4.2 Unhedged terminal payoff

Same identity as the long combo:

$$
f_T = (S_T - K_1)_+ - (K_2 - S_T)_+ - H
$$

`payoff` implements this and **ignores** the hedge. Hedged specs must still pass the unhedged grid with the hedge stripped. If you mix hedge P&L into this function, acceptance tests versus `073` will fail and you will hide a crash.

### 4.3 Unhedged break-evens

If $H>0$:

$$
S^\ast = K_1 + H
$$

Debit combo: hurdle above the call. Same branch as `073`. Use only when you paid.

If $H<0$:

$$
S^\ast = K_2 + H
$$

Credit combo: hurdle below the put. The dead zone keeps the credit. This is the usual equity-skew case. Mixing the debit formula here invents a call-side hurdle that is not there.

If $H=0$:

$$
K_2 \le S^\ast \le K_1
$$

Loss if spot drops below the put wing, net of the skew credit. With $C$ equal to put premium minus call premium (a credit when puts are rich), that path is the region $S_T < K_2$ shifted by $H=-C$. The zero-premium shelf is a band, not a single print.

### 4.4 Unhedged max profit and loss

$$
P_{\max} = \text{unlimited}
$$

$$
L_{\max} = K_2 + H
$$

Unhedged extrema match `073`. Store unlimited profit and finite crash loss. Hedged books should *not* replace these with a vega notional and pretend $L_{\max}$ is gone.

### 4.5 Delta-hedged P&L

If you delta-hedge, do not use $f_T$ as the P&L. Carry a Greek book $\Delta, \Gamma, \Theta, \nu$ and mark the 25-delta (or 16-delta) risk-reversal. Residual risks are jumps, sticky-strike versus sticky-delta, and dividend gaps. Financing: stock longs cost the overnight rate; stock shorts earn the rebate net of borrow. A backtest that marks only option mids and ignores hedge carry will mis-state the skew harvest.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed index or equity options with a posted smile. 25-delta and 16-delta points must be interpolable. Without a smile this file cannot pick the wings it names.
2. **Wings.** Pick tenor 1m or 3m (the quoted RR points). Map 25-delta (default) or 16-delta to strikes $K_1$ (call) and $K_2$ (put), $K_1 > K_2$. Deltas from a surface dated $\le t_{\mathrm{fill}}$; a future-dated smile is look-ahead.
3. **Legs.** Buy 1 call $K_1$, sell 1 put $K_2$. Quantity $1:1$. Optional: compute net delta and hedge with stock or futures. The options are `073`; the optional hedge is this file’s extra.
4. **Premium.** Compute $H$ and the RR mark $\sigma_{\mathrm{call}}-\sigma_{\mathrm{put}}$ (or the desk’s sign convention). Reject if the smile does not show put-over-call richness unless the spec is explicitly directional. That reject is what keeps a “skew” book from being a disguised directional debit.
5. **Metrics.** Store unhedged $S^\ast$, $P_{\max}$, $L_{\max}=K_2+H$, and the RR mark. If hedged, store hedge shares and residual delta. Keep both views; do not drop unhedged $L_{\max}$ because a hedge exists.
6. **Blotter.** Emit the two option intents plus an optional hedge intent. Do not route live orders.
7. **Hold.** Unhedged: this is `073`. Hedged: rebalance delta on the spec’s schedule; never skip a crash print. Skipping the hedge on a down day is how a “skew” backtest quietly becomes a combo.

## 6. Execution protocol

- If unhedged, you are running a long combo. If hedged, you are running a skew book: mark the RR and the hedge. Report which. Mixing the labels is how crash P&L gets filed as “vol.”
- Never treat unhedged RR as “market-neutral vol.”
- Default wings: 25-delta; 16-delta is the tail alternative. Tenors 1m and 3m are the quoted RR points. Random tenors are not the quoted mark this file compares to.
- Size off $L_{\max}=K_2+H$ when unhedged, and off jump/gap risk when hedged. Vega notional alone understates a gap through the put.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask, and (if hedging) borrow status for stock or the futures contract used as the hedge
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier
- A smile or delta map so 25-delta / 16-delta wings are identified
- The quoted 25-delta (and 16-delta) risk-reversal mark if the thesis is hedged skew
- Dividends and rates for deltas, forwards, and American exercise
- At expiry or exit: settlement print, hedge fills, and early-exercise events

Not used by this spec: book value, earnings, SUE.

Unhedged identities are European-style claims. American early exercise can invalidate them. Hedged P&L is not $f_T$. A smile fitted through $t>t_{\mathrm{fill}}$ is look-ahead on both the wings and the RR mark.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| wings | 25-delta | 16-delta allowed |
| tenor | 1m or 3m | quoted RR points |
| quantity ratio | $1:1$ | long call, short put |
| hedge | off | on → delta-hedge; P&L is not $f_T$ |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.volatility_skew_long_risk_reversal` with:

1. `legs(spec) -> list[Leg]` — long call $K_1$, short put $K_2$, optional stock/futures hedge leg.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — unhedged $f_T$ exactly as written above (ignore the hedge in this function).
4. `metrics(spec) -> dict` — `S*`, `P_max`, `L_max`, debit/credit flag, RR mark; hedge flag.
5. `validate(spec)` — $K_1 > K_2$, qty $1:1$ on the options; unhedged $L_{\max}=K_2+H$ at $S_T=0$; $f_T(S^\ast)=0$ on the matching $H$ branch.
6. `blotter(spec) -> list[OrderIntent]` — options plus optional hedge; never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Unhedged crash.** Short put. $L_{\max}=K_2+H$. Same as `073`. Calling it a skew harvest does not change the gap.
- **Hedged jump.** Delta hedge does not kill a gap through the put wing. Sticky-strike versus sticky-delta P&L can dominate the RR mark. A crash day can print hedge slippage that swamps the skew coupon.
- **Dividend gaps** on the hedge and on American exercise. Ex-div on a stock hedge versus an index RR mark is a basis leak.
- **Naming.** Same legs as `073`; the hedge and the thesis are what differ. Sharing a payoff function is correct; sharing a P&L label is not.
- **Look-ahead smile.** Fitting 25-delta wings on a surface that includes later prints picks strikes and an RR mark the live book did not have.

## 11. Acceptance tests

- Unhedged grid $S_T$ from $0$ to $3S_0$: $f_T$ equals $(S_T-K_1)_+ - (K_2-S_T)_+ - H$.
- At $S_T=0$, $f_T=-(K_2+H)=-L_{\max}$.
- Break-even branch matches `073`: $H>0 \Rightarrow S^\ast=K_1+H$; $H<0 \Rightarrow S^\ast=K_2+H$.
- Reject $K_1 \le K_2$. A spec with `hedge=True` must still pass the unhedged $f_T$ tests with the hedge stripped.
- Adding a fee $\tau$ per option contract shifts unhedged $f_T$ by a constant and moves $S^\ast$ only through $H$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
