---
rank: 78
slug: long-box
title: "Long Box"
asset_class: "options"
style: "conversion / locked cash / tax-adjacent"
horizon: "Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries."
instruments: "listed equity or index options; underlying shares if a stock leg is required"
---

# 078. Long Box

| Field | Value |
|---|---|
| Popularity rank (this kit) | 78 of 101 |
| Why it sits here | The locked conversion: bull call spread plus bear put spread. Used for interest-rate / early-exercise arb and occasionally tax timing (tax timing is mentioned as a known use; do not implement tax evasion). |
| Aliases | box spread |
| Asset class | options |
| Style | conversion / locked cash / tax-adjacent |
| Typical horizon | Until option expiry, typically 1 week to 3 months. Calendar/diagonal trades span two expiries. |
| Instruments | listed equity or index options; underlying shares if a stock leg is required |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long an ITM put $K_1$, short an OTM put $K_2 < K_1$, long an ITM call $K_2$, short an OTM call $K_1$. Four legs, same expiry. Terminal payoff is cash $K_1 - K_2$ regardless of $S_T$. That is a synthetic long forward at $K_2$ against a synthetic short forward at $K_1$, or equivalently a bull call spread plus a bear put spread on the same strikes.

You are betting that the listed box is cheap versus the present value of $K_1-K_2$. You are not taking a view on spot. If the box is fairly priced, $P_{\max}$ is financing, not alpha. If $D > K_1-K_2$, you have locked a loss. Tax timing is a known historical use of boxes; it is out of scope and must not be implemented as evasion.

The typical user is a conversion desk or anyone comparing listed options to financing. Horizon matches the rate period, often 1 week to 3 months. Prefer European index options so early exercise cannot break the lock. Require a buffer after fees, not a one-tick edge. Skip if any of the four legs is a one-sided quote.

## 2. First principles

Four listed options, quantity $1:1:1:1$. The bear put spread is long $K_1$ put minus short $K_2$ put. The bull call spread is long $K_2$ call minus short $K_1$ call. Subtract the debit $D$:

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ + (S_T - K_2)_+ - (S_T - K_1)_+ - D
$$

This is the listed-leg sum you implement first. Each pair is a vertical. Together they should not depend on $S_T$. If a unit test sees a kink, a sign or strike is wrong. $D$ is cash at $t=0$; compare it to PV of the strike gap, not to spot.

Put-call cancellation on each strike turns a call minus a put into a forward. The $K_2$ pair is a long synthetic forward. The $K_1$ pair is a short synthetic forward. Their difference is the strike gap, independent of $S_T$:

$$
(K_1 - S_T)_+ - (S_T - K_1)_+ - \bigl[(K_2 - S_T)_+ - (S_T - K_2)_+\bigr] = K_1 - K_2
$$

This is two copies of the identity in `045`/`065`, subtracted. It holds pathwise at expiry for European options. American early exercise, a missing right, or unequal quantities all break it. The right-hand side has no $S_T$: that is the lock.

Therefore the box identity is

$$
f_T = K_1 - K_2 - D
$$

Flat in spot. Metrics have no $S^\ast$. The only question is whether this constant is positive after costs and financing. If an implementation’s listed-leg sum disagrees with this constant on a grid, stop.

Assume the usual profitable lock

$$
K_1 \ge K_2 + D
$$

This is the same inequality as $K_1-K_2-D \ge 0$. If it fails, you paid more than the strike gap and the lock is a loss. Trade only when the box is cheap versus $e^{-rT}(K_1-K_2)$, which is stricter than the undiscounted inequality once rates are positive.

Then the constant P&L is non-negative and

$$
P_{\max} = (K_1 - K_2) - D
$$

If $K_1 - K_2 - D > 0$ after costs, this is a locked cash-and-carry style profit, subject to early exercise, pin, and financing. If $D > K_1 - K_2$, the lock is a locked **loss**. There is no break-even in $S_T$ because $f_T$ does not depend on $S_T$.

**Payoff sketch.** Any $S_T$: $f_T$ is the same number, $K_1-K_2-D$. At $S_T=0$, at $S_T$ between the strikes, and far above $K_1$, the four intrinsics rearrange to the strike gap minus $D$. If the sketch is not a horizontal line, the legs are wrong. The interesting plot is $D$ versus $e^{-rT}(K_1-K_2)$, not $f_T$ versus spot.

That is the whole strategy. You are trading the box versus the present value of $K_1-K_2$, not a view on spot.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K_2 < K_1$ | lower strike (long call, short put) and higher strike (long put, short call) |
| $(x)_+$ | $\max(x,0)$ |
| $D$ | net debit paid at $t=0$ |
| $f_T$ | terminal P&L including $D$; constant in $S_T$ |
| $P_{\max}$ | locked profit $(K_1-K_2)-D$ when that quantity is positive |

Same expiry all four legs. Quantity one-lot each. This file uses $K_1$ as the **higher** strike.

## 4. Mathematics

### 4.1 Premium

$D$ is the net debit of the four listed legs. Compare $D$ to the present value of $K_1-K_2$, not to spot. Fill all four at bid/ask. A mid-to-mid “cheap box” is the usual look-ahead. Clearing fees belong in $D$ before you claim an edge.

### 4.2 Terminal payoff from the legs

$$
f_T = (K_1 - S_T)_+ - (K_2 - S_T)_+ + (S_T - K_2)_+ - (S_T - K_1)_+ - D
$$

Always compute this sum in tests. Permuting $S_T$ must not change the value. If it does, a right or a sign is wrong. This is the definition of the lock from the blotter, before you collapse to $K_1-K_2-D$.

### 4.3 Box identity

$$
f_T = K_1 - K_2 - D
$$

The identity holds for every $S_T$ on European options with no early exercise. Use it in `payoff` as the closed form *and* check it against the listed-leg sum. American assignment makes both expressions fiction until you flatten.

### 4.4 Locked profit

When $K_1 \ge K_2 + D$:

$$
P_{\max} = (K_1 - K_2) - D
$$

There is no $S^\ast$ because $f_T$ is flat. If $D > K_1-K_2$, $P_{\max}$ is negative: a locked loss. Do not emit a break-even in spot. The economic edge after financing is $e^{-rT}(K_1-K_2)-D$, which can be negative even when undiscounted $P_{\max}$ is positive.

### 4.5 Mark-to-market and financing

Before expiry, mark is the sum of option mids minus initial $D$. European boxes should trade near $e^{-rT}(K_1-K_2)$. American early exercise can destroy the lock. Accrue interest on the cash used to pay $D$; the economic edge is $e^{-rT}(K_1-K_2) - D$ after costs, not the undiscounted $P_{\max}$. Do not use this file as a tax-avoidance recipe.

## 5. Step-by-step algorithm

1. **Universe.** Liquid listed calls and puts at two strikes, same expiry. Tight markets on all four legs; skip if any leg is a one-sided quote. A missing bid on the short call makes $D$ fiction and the lock untradeable.
2. **Strikes.** $K_1 > K_2$, typically spanning ATM. Same $T$. This file’s $K_1$ is the higher strike; do not relabel to textbook $K_1<K_2$ without flipping the legs.
3. **Legs.** Buy put $K_1$, sell put $K_2$, buy call $K_2$, sell call $K_1$. One-lot each. That is bear put plus bull call. Any other combination is a condor or a reversal, not a box.
4. **Premium.** Compute $D$. Compare to $e^{-rT}(K_1-K_2)$. Trade only if the box is cheap (long box) or rich (you would sell the box — not this file). Skipping the PV comparison books undiscounted “alpha” that is just carry.
5. **Metrics.** Store $f_T = K_1-K_2-D$ and $P_{\max}=(K_1-K_2)-D$. No $S^\ast$. If $P_{\max}<0$, the lock is a loss; do not emit a buy.
6. **Blotter.** Enter as one four-leg box ticket. Do not route live orders. Legging two verticals separately can break the lock intra-day.
7. **Hold.** Hold to $T$ if European. Flatten immediately on American assignment; the lock is broken. After assignment you have a stock residual plus three options, not a box.

## 6. Execution protocol

- Only trade if the box is cheap versus the present value of $K_1-K_2$. Fair boxes are financing, not a directional edge.
- American options: early exercise can destroy the lock. Prefer European index options for the identity.
- Clearing fees, pin, and exercise can eat $K_1-K_2-D$. Require a buffer, not a one-tick edge. A backtest at mid with zero fees will “lock” ticks that never survive the four-leg spread.
- Do not implement tax evasion. Tax timing is a known historical use of boxes; it is out of scope for this spec.

## 7. Data contract

Required, point-in-time:

- Underlying last, bid, ask
- Option chain at one expiry: bid/ask, strike, call/put flag, open interest, implied vol, multiplier — **call and put at $K_1$ and at $K_2$**
- Financing rate $r$ (and dividends if American / if you mark to a model)
- At expiry: settlement print and any early-exercise events

Not used by this spec: book value, earnings, SUE, a directional signal.

These identities are European-style claims. American early exercise can invalidate them. Delay-0 mids for $D$ are research-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| strikes | spanning ATM, $K_1 > K_2$ | same expiry |
| quantity | one-lot each | four legs |
| tenor | match the financing horizon | typically 1 week to 3 months |
| entry rule | $D < e^{-rT}(K_1-K_2)$ minus costs | locked edge |
| delay | 1 bar | delay-0 mid is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.long_box` with:

1. `legs(spec) -> list[Leg]` — long put $K_1$, short put $K_2$, long call $K_2$, short call $K_1$, $K_1 > K_2$.
2. `net_premium(legs, quotes) -> float` — signed cash at $t=0$ (credit positive).
3. `payoff(s_t, spec) -> float` — implements both the listed-leg sum and $K_1-K_2-D$.
4. `metrics(spec) -> dict` — `P_max`, debit flag; `S*` is absent (constant payoff).
5. `validate(spec)` — strike order $K_1 > K_2$; on a dense $S_T$ grid, $f_T$ is constant and equals $K_1-K_2-D$.
6. `blotter(spec) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access. Refuse tax-evasion features.

## 10. Risks and failure modes

- **Early exercise.** American assignment breaks $f_T = K_1-K_2-D$. A dividend on the short call is the usual path; after assignment you are not in a box.
- **Pin and fees.** Clearing fees can eat $K_1-K_2-D$. Pin at either strike can leave a residual stock position from one-sided exercise.
- **Not a directional edge.** If the box is fairly priced, $P_{\max}$ is financing, not alpha. Booking undiscounted $K_1-K_2-D$ as return ignores the cash tied up in $D$.
- **Locked loss.** Buying a rich box locks in $D-(K_1-K_2)<0$. Mid-to-mid entry is how that happens in a backtest that looks profitable.
- **Tax misuse.** Do not add features whose purpose is to hide income or wash a gain. Mention of tax timing in the literature is not a spec to code.

## 11. Acceptance tests

- Grid $S_T$ from $0$ to $3S_0$: listed-leg $f_T$ is constant and equals $K_1-K_2-D$.
- $P_{\max}=(K_1-K_2)-D$ matches that constant.
- Reject $K_1 \le K_2$ or a missing right at either strike.
- Adding a fee $\tau$ per contract shifts the constant $f_T$ and does not create a kink in $S_T$.
- Permuting $S_T$ must not change $f_T$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
