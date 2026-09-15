---
rank: 10
slug: long-iron-condor
title: "Long Iron Condor"
asset_class: "options"
style: "sideways / income / defined risk"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 010. Long Iron Condor

| Field | Value |
|---|---|
| Popularity rank (this kit) | 10 of 101 |
| Why it sits here | The defined-risk short-vol structure that replaced naked strangles in most retail and many systematic vol-sell programs. |
| Aliases | — |
| Asset class | options |
| Style | sideways / income / defined risk |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Bull put spread plus bear call spread: long OTM put $K_1$, short OTM put $K_2$, short OTM call $K_3$, long OTM call $K_4$, equidistant strikes $\kappa$. Net credit. Neutral income.

You are betting that $S_T$ finishes inside $[K_2,K_3]$ so every option dies and you keep $C$. You are not betting on a large move, and you are not running a naked short strangle. The long wings cap the loss at $\kappa-C$. You are also not running a small-risk trade just because the risk is defined: $L_{\max}$ can still be most of the wing. This file's "long" iron condor is the **credit** structure (short the inner wings). Some brokers call the same payoff a short iron condor. Match the payoff, not the name.

Payoff sketch, one lot, ignore financing: at $S_T=0$ both puts are in the money, the calls are dead, and $f_T=C-\kappa=-L_{\max}$. At an inner strike ($S_T=K_2$ or $S_T=K_3$) you are at the edge of the plateau and $f_T=C=P_{\max}$. Far above $K_4$ both calls are in the money, the puts are dead, and $f_T=C-\kappa=-L_{\max}$ again.

## 2. First principles

A long put at $K_1$ and a short put at $K_2>K_1$ are the bull put spread:

$$
(K_1 - S_T)_+ - (K_2 - S_T)_+
$$

That vertical is the left engine. Above $K_2$ it is zero. Below $K_1$ it is worth $K_1-K_2=-\kappa$. Between the two strikes it slopes with the short put. You sell the inner put and buy the wing so a crash cannot take more than $\kappa$ on this side, before the credit.

A short call at $K_3$ and a long call at $K_4>K_3$ are the bear call spread:

$$
-(S_T - K_3)_+ + (S_T - K_4)_+
$$

That vertical is the right engine. Below $K_3$ it is zero. Above $K_4$ it is worth $-\kappa$. Together the two verticals are a short strangle with a long strangle around it. Equal $\kappa$ on both sides is this file's default; unequal wings are a broken condor and a different $L_{\max}$ on each tail.

Receiving a net credit $C$ at $t=0$ and adding both verticals is the long (credit) iron condor:

$$
f_T = (K_1 - S_T)_+ + (S_T - K_4)_+ - (K_2 - S_T)_+ - (S_T - K_3)_+ + C
$$

$C$ must be less than $\kappa$ or there is no positive $P_{\max}$ after a complete wing loss. $C$ is the net of four fills, not four mids. Inside $[K_2,K_3]$ every option expires worthless and you keep $C$. Outside the wings the long option pays, but only after the short option has already lost the wing width $\kappa$. You sold a strangle and bought a further strangle so the loss cannot exceed $\kappa-C$.

This file’s “long” iron condor is that **credit** structure (short the inner wings). Some brokers call the same payoff a short iron condor. Match the payoff, not the name.

That is the whole strategy. Everything below is just how to pick the four strikes, how to keep $C<\kappa$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1<K_2<K_3<K_4$ | strikes, increasing |
| $\kappa$ | wing width, $K_4-K_3=K_3-K_2=K_2-K_1$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

All four legs share expiry $T$ and quantity $1$. Structure so $C < \kappa$.

## 4. Mathematics

### 4.1 Terminal payoff

Equidistant strikes: $K_4 - K_3 = K_3 - K_2 = K_2 - K_1 = \kappa$.

Four listed intrinsics plus the credit:

$$
f_T = (K_1 - S_T)_+ + (S_T - K_4)_+ - (K_2 - S_T)_+ - (S_T - K_3)_+ + C
$$

The plateau is $[K_2,K_3]$ at height $C$. The slopes are the short inner options. The floors outside the wings are $C-\kappa$. Sketch: $S_T=0$ prints $-L_{\max}$; at $K_2$ or $K_3$ prints $P_{\max}$; far above $K_4$ prints $-L_{\max}$. Tests must keep the four signs as written; flipping an inner short into a long is the debit condor.

### 4.2 Break-evens

On the call side, the short call starts losing at $K_3$ and $f_T=0$ at

$$
S^\ast_{\mathrm{up}} = K_3 + C
$$

A rally of $C$ through the short call strike eats the credit. Beyond that you lose until the long call at $K_4$ stops the bleed. If $C$ is small relative to $\kappa$, the up-side break-even sits close to $K_3$ and most of the wing is a losing region.

On the put side, the short put starts losing at $K_2$ and $f_T=0$ at

$$
S^\ast_{\mathrm{down}} = K_2 - C
$$

Symmetric on the left. A crash of $C$ through $K_2$ eats the credit. The profitable band is $(K_2-C,\,K_3+C)$, which is wider than the inner plateau by $C$ on each side. That band is still much narrower than "the stock did not go to zero."

### 4.3 Extrema

Maximum profit is the credit, attained for $S_T \in [K_2,K_3]$:

$$
P_{\max} = C
$$

That is the whole designed outcome: time passes, spot sits, four options die. Mark-to-market before expiry can be less than $C$ even on that path if implied vol rises. Expiry $P_{\max}$ is not a live floor under the mark.

Maximum loss is the wing width net of the credit, attained for $S_T \le K_1$ or $S_T \ge K_4$:

$$
L_{\max} = \kappa - C
$$

A complete test of either wing realizes this number. For a $\$5$ wing and a $\$1.20$ credit, $L_{\max}=\$3.80$ per share, times $m$. Defined is not small. Ratioing a wing (more shorts than longs) destroys this bound.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with four tight strikes around spot. Open interest on all four legs above a minimum. A missing wing is a naked vertical, not a condor. Indexes usually have cleaner four-strike grids than single names.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ must sit between $K_2$ and $K_3$ for the default OTM condor. A later print can re-center the structure and look-ahead the credit.
3. **Strikes.** Choose $K_1<K_2<K_3<K_4$ with equal spacing $\kappa$, $K_2<S_0<K_3$. Default: equal $\kappa$, or 16-delta inners and 5-delta outers (not equidistant; then replace $\kappa$ with the actual short-to-long width on each side). Equal $\kappa$ is what this file's $L_{\max}$ formula assumes. Delta wings must use the actual widths, possibly different on each side.
4. **Expiry.** Same $T$ on all four legs. Typical 1 week to 3 months. Mixed expiries are two calendars, not this payoff. Short-dated condors harvest more theta and take more gamma into expiry.
5. **Size.** One-lot each. Do not ratio a wing. A short inner without its long wing is a naked strangle with this file's name on it.
6. **Premium.** $C$ is the net credit actually received. Reject the ticket if $C \ge \kappa$. A credit as large as the wing means you are being paid to take a riskless-looking box that is either mis-struck or too good to be a listed fill.
7. **Blotter.** Emit a four-legged net-credit intent. Do not route live orders. One ticket keeps the four fills together.
8. **Hold / manage.** Hold to expiry, or manage at 50% of max credit, or if a test of $K_2$ or $K_3$ occurs. Management is an overlay; it is not part of expiry $f_T$. Closing early crystallizes a mark, not $C$ or $\kappa-C$.

## 6. Execution protocol

- Enter as a four-legged order with a net-credit limit. Do not leg a short inner without the long wing already on.
- Document the spec-vs-broker naming clash in the module docstring: this payoff is the credit iron condor.
- Assignment risk on short American options into expiry and into ex-dates.
- Cap lots by ADV and by $L_{\max}\times m$.

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
| spacing | equal $\kappa$ | 16-delta / 5-delta alternative is not equidistant |
| inners | OTM, $K_2<S_0<K_3$ | short put and short call |
| quantity | $1:1:1:1$ | one-lot each |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_iron_condor` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1<K_2<K_3<K_4$; equal $\kappa$ when the spec claims equidistant; $C<\kappa$; $P_{\max}=C$ and $L_{\max}=\kappa-C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined, not small.** $L_{\max}=\kappa-C$ can be a large fraction of $\kappa$. A $\$10$ wide condor for a $\$1.50$ credit still loses $\$8.50$ per share on a wing test, times $m$. Sizing off $C$ rather than $L_{\max}$ is the usual blow-up.
- **Assignment.** Short American puts and calls can be exercised early. A short inner put assigned overnight turns that side into a long stock you did not want, while the long wing is still a put.
- **IV expansion.** Mark-to-market can breach $L_{\max}$ in spirit before expiry even though expiry $L_{\max}$ is capped. A vol spike widens both short options; you can be stopped out of a trade that would have expired at $C$.
- **Naming clash.** Implementing the debit (short) iron condor under this module name flips every sign. The plateau becomes a trough. Tests on $P_{\max}=C$ will fail loudly if you got this right; if they pass with a debit, the signs are wrong.
- **Broken wing.** Unequal $\kappa$ without rewriting $L_{\max}$ reports the wrong cap on one tail. Delta-based wings need the actual short-to-long width on each side.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals the sum of the four listed intrinsics plus $C$.
- For $S_T \in [K_2,K_3]$, $f_T=C=P_{\max}$. For $S_T\le K_1$ or $S_T\ge K_4$, $f_T=C-\kappa=-L_{\max}$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- Reject a spec that violates $K_1<K_2<K_3<K_4$, unequal quantities, or $C\ge\kappa$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
