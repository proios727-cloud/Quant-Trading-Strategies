---
rank: 42
slug: long-iron-butterfly
title: "Long Iron Butterfly"
asset_class: "options"
style: "sideways / credit"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 042. Long Iron Butterfly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 42 of 101 |
| Why it sits here | Credit butterfly: short ATM straddle plus long OTM strangle. Standard defined-risk pin trade. |
| Aliases | — |
| Asset class | options |
| Style | sideways / credit |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long OTM put $K_1$, short ATM put and ATM call $K_2$, long OTM call $K_3$, $\kappa = K_2-K_1 = K_3-K_2$. Net credit. Neutral income.

You are betting that $S_T$ pins $K_2$ so the short straddle dies and the wings die and you keep $C$. You are not running a naked short straddle: the wings cap the loss at $\kappa-C$. You are not running a debit call butterfly; this file is a credit structure (short the body). Some brokers call the same payoff a short iron butterfly. Match the payoff, not the name. Defined is not small: $L_{\max}$ can be most of the wing.

Payoff sketch, one lot, ignore financing: at $S_T=0$ the long put pays $K_1$, the short put costs $K_2$, the calls die, and $f_T=C-\kappa=-L_{\max}$. At $S_T=K_2$ every option expires worthless and $f_T=C=P_{\max}$. Far above $K_3$ the long call pays after the short call has already lost $\kappa$, and $f_T=C-\kappa=-L_{\max}$ again.

## 2. First principles

A short ATM straddle at $K_2$ is a short put plus a short call:

$$
-(K_2 - S_T)_+ - (S_T - K_2)_+
$$

That is the inverted V of the short straddle. Alone it is unbounded. The iron butterfly exists to buy wings around it. The body is one short put and one short call at the same $K_2$, not two short calls.

A long OTM put at $K_1<K_2$ and a long OTM call at $K_3>K_2$ are the wings:

$$
(K_1 - S_T)_+ + (S_T - K_3)_+
$$

That is a long strangle. Below $K_1$ the put pays; above $K_3$ the call pays. Equal $\kappa$ makes each wing stop the body after the same distance. Unequal $\kappa$ is a broken iron fly.

The straddle credit exceeds the wing debit, so the package is a net credit $C$ at $t=0$. Adding the five pieces is the long (credit) iron butterfly:

$$
f_T = (K_1-S_T)_+ - (K_2-S_T)_+ - (S_T-K_2)_+ + (S_T-K_3)_+ + C
$$

$C$ must be less than $\kappa$. At $S_T=K_2$ every option expires worthless and you keep $C$. Outside the wings the long option pays, but only after the short straddle has already lost the wing width $\kappa$. Loss cannot exceed $\kappa-C$. This file’s “long” iron butterfly is that **credit** structure. Some brokers call the same payoff a short iron butterfly. Match the payoff, not the name.

That is the whole strategy. Everything below is how to keep equal $\kappa$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_1 < K_2 < K_3$ | OTM put, ATM body, OTM call |
| $\kappa$ | wing width, $K_2-K_1 = K_3-K_2$ |
| $C$ | net credit received at $t=0$ |
| $f_T$ | terminal P&L including $C$ |
| $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens, $f_T=0$ |
| $P_{\max}$, $L_{\max}$ | expiry max profit and max loss, ignoring financing and fees |
| $m$ | option multiplier (usually $100$) |

Quantity $1$ on each of the four contracts (the body is one short put and one short call at the same $K_2$). Same expiry $T$. Structure so $C < \kappa$.

## 4. Mathematics

### 4.1 Terminal payoff

Long put $K_1$, short put $K_2$, short call $K_2$, long call $K_3$, net credit $C$:

$$
f_T = (K_1-S_T)_+ - (K_2-S_T)_+ - (S_T-K_2)_+ + (S_T-K_3)_+ + C
$$

Peak at $K_2$ of height $C$, floors outside the wings at $C-\kappa$. Tests must keep four signs and a shared body strike. Sketch: $S_T=0$ prints $-L_{\max}$; at $K_2$ prints $C$; far above $K_3$ prints $-L_{\max}$.

### 4.2 Break-evens

On the call side, $C-|S_T-K_2|=0$ near the body with $S_T>K_2$:

$$
S^\ast_{\mathrm{up}} = K_2 + C
$$

A rally of $C$ through the body eats the credit. The wing at $K_3$ only stops the loss later. If $C$ is small relative to $\kappa$, most of the right wing is a losing region. This break-even is the short-straddle break-even; the wings do not move it.

On the put side:

$$
S^\ast_{\mathrm{down}} = K_2 - C
$$

Symmetric. The profitable band is $(K_2-C,\,K_2+C)$, the same width as a short straddle's band, with a floor outside the wings the straddle does not have. That is the whole point of paying for the strangle.

### 4.3 Extrema

Maximum profit is the credit, attained at $S_T=K_2$:

$$
P_{\max} = C
$$

Pin is the designed outcome. Unlike the short straddle, a miss that runs past a wing is capped. Unlike the call butterfly, you received $C$ rather than paying $D$, so the peak is a credit, not $\kappa-D$.

Maximum loss is the wing width net of the credit, attained for $S_T \le K_1$ or $S_T \ge K_3$:

$$
L_{\max} = \kappa - C
$$

A complete test of either wing realizes this number. For a $\$10$ wing and a $\$6$ credit, $L_{\max}=\$4$ per share, times $m$. ATM gamma still dominates the live mark even though expiry $L_{\max}$ is defined.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed names or indexes with an ATM straddle and OTM wings. Open interest on the body above a minimum. A missing wing is a naked short straddle. The body is two ATM options; that is the fill and the gamma.
2. **Spot.** Record $S_0$ from a timestamp $\le t_{\mathrm{fill}}$. $S_0$ places $K_2$ ATM. A later print look-aheads $C$ and the pin.
3. **Strikes.** Short ATM straddle at $K_2\approx S_0$. Buy OTM put $K_1$ and OTM call $K_3$ with equal $\kappa$. Unequal $\kappa$ needs two $L_{\max}$ numbers, not this file's one.
4. **Expiry.** Same $T$ on all four contracts. Mixed expiries are not an iron butterfly. Short-dated bodies have violent gamma into the pin.
5. **Size.** One-lot each. Do not ratio a wing. Extra shorts on the body without extra longs on the wings restore unbounded tails.
6. **Premium.** $C$ is the net credit actually received. Reject if $C \ge \kappa$. A credit as large as the wing is a mis-struck ticket or a mid fiction.
7. **Blotter.** Emit a four-legged iron-butterfly intent. Do not route live orders. One ticket keeps the short straddle from going on without the wings.
8. **Hold.** Pin at $K_2$ is the designed peak. Often cheaper to execute than a call butterfly when puts are rich. Early management is an overlay; ATM gamma can force it even when expiry $L_{\max}$ looks comfortable.

## 6. Execution protocol

- Same naming clash as iron condors. Match payoff. Document it in the module docstring.
- Enter as one ticket. Do not short the ATM straddle without the wings on.
- Short ATM options have high gamma into expiry; that is the live risk even though expiry $L_{\max}$ is defined.
- Cap lots by $L_{\max}\times m$ and by ADV on the body.

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
| body $K_2$ | ATM | short straddle |
| $\kappa$ | equal wings | $K_2-K_1=K_3-K_2$ |
| quantity | $1:1:1:1$ | put $K_1$, put $K_2$, call $K_2$, call $K_3$ |
| $m$ | $100$ | US equity listed default |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_iron_butterfly` with:

1. `legs(spec) -> list[Leg]` — each `Leg` has `side` (long/short), `right` (call/put/stock), `strike`, `expiry`, `qty`.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive). Matches $C$.
3. `payoff(s_t, spec) -> float` — implements $f_T$ exactly as written in this file.
4. `metrics(spec) -> dict` — `S*_up`, `S*_down`, `P_max`, `L_max`, debit/credit flag.
5. `validate(spec)` — $K_1<K_2<K_3$ and $K_2-K_1=K_3-K_2$; $C<\kappa$; $P_{\max}=C$ and $L_{\max}=\kappa-C$ on a dense $S_T$ grid.
6. `blotter(spec) -> list[OrderIntent]` — ticker, side, quantity, limit, TIF. Never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Defined, not small.** $L_{\max}=\kappa-C$ can be most of the wing. A $\$5$ iron fly for a $\$1.50$ credit still loses $\$3.50$ per share on a wing test, times $m$. Sizing off $C$ is the usual blow-up.
- **ATM gamma.** The short straddle dominates mark-to-market into expiry. You can be stopped out of a trade that would have expired at $C$ because the live mark looked like a naked straddle.
- **Naming clash.** Implementing the debit iron butterfly under this module name flips every sign. The peak becomes a trough. Tests on $P_{\max}=C$ at $S_T=K_2$ exist to catch this.
- **Assignment.** Short American ATM options can be exercised early. A short ATM put assigned overnight leaves you long stock against a short ATM call and a long OTM strangle — a mess that is not $f_T$.
- **Broken wings.** Unequal $\kappa$ without rewriting $L_{\max}$ reports the wrong cap on one tail.

## 11. Acceptance tests

- On a grid $S_T$ from $0$ to $3S_0$, $f_T$ equals $(K_1-S_T)_+-(K_2-S_T)_+-(S_T-K_2)_++(S_T-K_3)_++C$.
- Break-evens: $f_T(S^\ast_{\mathrm{up}})=f_T(S^\ast_{\mathrm{down}})=0$ within $10^{-8}$ relative to $S_0$.
- At $S_T=K_2$, $f_T=C=P_{\max}$. For $S_T\le K_1$ or $S_T\ge K_3$, $f_T=C-\kappa=-L_{\max}$.
- Reject a spec that violates $K_1<K_2<K_3$, unequal $\kappa$, or $C\ge\kappa$.
- Adding a fee $\tau$ per contract shifts $f_T$ by a constant and does not move the kinks except through $C$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
