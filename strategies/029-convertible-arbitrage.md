---
rank: 29
slug: convertible-arbitrage
title: "Convertible Arbitrage"
asset_class: "convertibles / equity"
style: "long cheap convert vs short stock"
horizon: "6–12 months from issuance; daily hedge update"
instruments: "convertible bond; issuer common stock"
---

# 029. Convertible Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 29 of 101 |
| Why it sits here | The classic hedge-fund relative-value book: buy underpriced converts, short delta shares. Core ‘hf’ style since the 1990s. |
| Aliases | convert arb, delta-hedged convertible, long cheap convert |
| Asset class | convertibles / equity |
| Style | long cheap convert vs short stock |
| Typical horizon | 6–12 months from issuance; daily hedge update |
| Instruments | convertible bond; issuer common stock |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A convertible bond is a credit-sensitive coupon bond plus the right to exchange it for a fixed number of issuer shares. New issues often print cheap versus a model that values those two pieces separately and adds them. The working book is: buy the cheap bond, short enough common stock to cancel the embedded-option delta, and refresh that hedge as the stock moves so that the residual is cheapness, carry, and gamma rather than a stock call.

You are betting that the market price sits below a model you froze before the fill, and that a share overlay can strip the first-order equity so the gap can close, coupons can accrue, and discrete re-hedging can harvest convexity. You are not betting that the issuer’s stock goes up. You are not buying the credit spread for its own sake, and you are not running a naked long-volatility option. A convert that is cheap only because the model used a later vol, a later CDS print, or the same stock tick you are about to trade is not this strategy.

Cheapness is largest around issuance for many names, which is why the default hold is the first 6–12 months of the bond’s life rather than a perpetual inventory. The stock hedge is daily (or banded) because delta is not a constant: it rises as the stock rallies toward conversion and falls as the bond trades toward the credit floor. If you cannot locate the shares, you do not buy the bond. If you lose the locate later, the book becomes a long-credit, long-equity residual — the 2008 failure mode in miniature.

## 2. First principles

Ignore callability and default for one identity. The holder may surrender the bond and receive $C$ shares. The package is therefore a straight bond plus a conversion option $V(S)$ on the issuer’s stock $S$:

$$
P_C^{\ast} = P_B + V(S)
$$

$P_B$ is the bond floor: coupons and principal discounted on the issuer’s credit curve. $V(S)$ is the conversion option (model-dependent: binomial, Tsiveriotis–Fernandes, or equivalent). The split is an accounting identity inside a chosen model, not a claim that the market quotes those two pieces separately. Callability, puts, and takeout language sit inside $V$ or as a separate Bermudan overlay; they are not optional extras you can ignore after the identity is written. Default couples $P_B$ to $S$ in a full credit-equity model, which is why the hedge later uses the model’s total delta rather than the equity-only slice of $V$.

Market cheapness is the gap between that theoretical value and the traded dirty price:

$$
\chi = P_C^{\ast} - P_C^{\mathrm{mkt}}
$$

$\chi > 0$ means the convert is cheap relative to the frozen model. $\chi < 0$ means it is rich; this spec does not buy rich converts in the hope that they cheapen further. The gap is in dirty-price units, so accrued must sit on both sides or on neither — mixing clean theoretical value against dirty market is a different, invalid $\chi$. Bid/ask, expected borrow, and credit carry come out of $\chi$ before the screen, not after you are already long.

Buy one bond. The stock sensitivity of the theoretical package is the option delta times the conversion ratio. The option delta is

$$
\Delta = \partial V / \partial S
$$

Delta is the first derivative of the conversion option with respect to the stock, evaluated at the frozen inputs. It is a number between roughly 0 (deep credit, option nearly worthless) and 1 per share in the option measure, then scaled by $C$ into a share count. Bump-and-revalue and an analytic derivative must agree to the model’s tolerance; mixing a binomial delta with a closed-form cheapness is a specification bug. $\Delta$ is computed at $t-\varepsilon$, not at the fill print.

and the share hedge per bond is

$$
h = \Delta \times C
$$

$C$ is the contractual conversion ratio: shares delivered per bond on conversion, not a delta-adjusted share count. Multiplying $\Delta$ by $C$ turns an option derivative into a stock overlay the blotter can short. If $C$ changes on a corporate action, $h$ must be rebuilt from the new ratio and a new model snapshot; do not scale the old hedge by a split factor and call it the same book. $h$ is positive when you are long the convert and short stock.

Long one bond and short $h$ shares. Instantaneous equity exposure cancels:

$$
\frac{\partial P_C^{\ast}}{\partial S} - h = \Delta\,C - \Delta\,C = 0
$$

The identity says the theoretical package’s stock slope equals the share overlay, so a tiny $dS$ does not change the hedged mark through first order. It does not say the market price $P_C^{\mathrm{mkt}}$ has the same delta as the model; residual market delta is a basis you live with inside a band. It also does not cancel credit, rates, or vol. (In a full credit-equity model $P_B$ also moves with $S$ through default. Use the model’s **total** delta, not the equity-only split.)

A small stock move $dS$ then leaves the quadratic (gamma) piece. With $\Gamma = \partial^2 V / \partial S^2$,

$$
dV - \Delta\,dS \approx \Theta\,dt + \tfrac12 \Gamma\,(dS)^2
$$

The left-hand side is the option P&L after the delta hedge: theta over the clock and gamma on the squared move. Long the convert is typically long gamma when the option is live, so discrete re-hedging can earn the $\tfrac12 \Gamma (dS)^2$ term if you actually trade the stock toward the new $h$. Theta and financing work the other way: you pay to sit. Credit deterioration can crush $P_B$ while the short stock rallies — that is the 2008 failure mode, and it is outside this second-order expansion.

The hedged book therefore earns: (i) cheapness $\chi$ if the market converges to the model, (ii) bond carry minus stock borrow and financing, (iii) long gamma if you re-hedge. None of those three is guaranteed on a given name. $\chi$ can widen after you buy; borrow can be recalled; gamma is small when the bond is deep credit or already converted in all but name.

That is the whole strategy. Everything below is how to measure $\Delta$, how to band the hedge, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $C$ | conversion ratio (shares delivered per bond) |
| $S$ | issuer common-stock price |
| $P_B$ | straight-bond present value (bond floor) |
| $V(S)$ | conversion-option value from the documented model |
| $P_C^{\ast}$ | theoretical convertible value $P_B + V(S)$ |
| $P_C^{\mathrm{mkt}}$ | market dirty price of the convert |
| $\chi$ | cheapness $P_C^{\ast} - P_C^{\mathrm{mkt}}$ |
| $\Delta = \partial V / \partial S$ | conversion-option delta |
| $\Gamma = \partial^2 V / \partial S^2$ | conversion-option gamma |
| $h$ | shares short per long bond, $h = \Delta \times C$ |
| $h_{\mathrm{tgt}}$ | target hedge from the latest model snapshot |
| $I$ | gross dollars on the convert leg |

## 4. Mathematics

### 4.1 Conversion option and delta

Fix a pricing model and freeze every input (curve, credit, borrow, dividends, call schedule) at a timestamp strictly before the fill. The conversion option value $V(S)$ is that model’s output. Delta is the stock derivative of $V$:

$$
\Delta = \partial V / \partial S
$$

Compute $\Delta$ by bump-and-revalue or by the model’s analytic derivative. Do not mix models between the cheapness screen and the hedge. The freeze is load-bearing: a Treasury curve, issuer CDS, borrow fee, or dividend forecast that prints after $t-\varepsilon$ must not enter $V$ or $\Delta$ for a fill at $t$. If the model needs a vol surface, that surface is dated $\le t-\varepsilon$ as well; using the close-of-day implied vol after you already decided to buy is look-ahead. Document one model for the whole test window.

### 4.2 Hedge ratio

One bond is exchangeable into $C$ shares, so the share overlay is

$$
h = \Delta \times C
$$

The book is: long 1 bond, short $h$ shares. $\Delta$ (and $\Gamma$) move with $S$, so $h$ is not a set-and-forget share count. Optional gamma overlay: when $\lvert \Gamma \rvert$ is large, tighten the hedge band so that discrete rebalancing captures more of $\tfrac12 \Gamma (dS)^2$. When $\lvert \Gamma \rvert$ is small, a wide band avoids churning the stock for noise. The band is a share threshold on $\lvert h - h_{\mathrm{tgt}} \rvert$, not a percentage of ADV, unless you document a translation.

### 4.3 Cheapness screen

Trade only converts with $\chi$ above a threshold after bid/ask, borrow, and expected credit carry. Default: start at the issue date, when cheapness is typically largest. The screen is not a forecast that $\chi$ will close this week; it is a filter that refuses rich and barely-cheap names after costs. Names that pass only because the model used a dividend cut that had not been announced are not in the universe.

### 4.4 Holding-period P&L

Over a mark-to-market interval, with $Q_{\mathrm{bond}}$ bonds and $Q_{\mathrm{shr}} = -h\,Q_{\mathrm{bond}}$ shares,

$$
\mathrm{P\&L} = Q_{\mathrm{bond}}\,\Delta P_C^{\mathrm{mkt}} + Q_{\mathrm{shr}}\,\Delta S + \mathrm{coupons} - \mathrm{borrow} - \mathrm{financing} - \mathrm{costs}
$$

The first term is the convert mark, dirty, including any pull-to-par or credit move. The second is the stock overlay; with $Q_{\mathrm{shr}}<0$ a rally in $S$ hurts. Coupons are cash on the bond; borrow and financing are cash on the short stock and on the bond inventory. Report net return on convert-leg gross $I$, and the residual delta after the hedge (should be near zero inside the band). Residual delta outside the band is an unhedged issuance-flip, not a rounding error.

## 5. Step-by-step algorithm

1. **Universe.** Listed convertible bonds with a quoted conversion ratio $C$, a locate on the issuer’s common, and a documented pricing model. Drop issues with missing call schedules or missing credit input. This step exists so you never price a Bermudan as a European, and so you never buy a bond you cannot hedge.
2. **Model snapshot.** At $t-\varepsilon$, freeze the Treasury curve, issuer credit curve, borrow fee, dividend forecast, and call/put schedule. Price $P_C^{\ast} = P_B + V(S)$ and $\Delta = \partial V / \partial S$. This step exists to kill look-ahead: the fill must not see the same print that just moved $S$, CDS, or vol.
3. **Screen.** Compute $\chi$. Keep names with $\chi$ above the cheapness threshold after estimated costs. Prefer new issues in the first 6–12 months. This step exists so the book is a cheapness harvest, not an unfiltered long-convert inventory.
4. **Hedge.** Set $h = \Delta \times C$. Short $h$ shares per long bond. If borrow is unavailable, **do not** put on the long convert. This step exists because an unhedged convert is a directional credit-and-equity bet, which this spec refuses.
5. **Band.** Rebalance the stock leg only when $\lvert h - h_{\mathrm{tgt}} \rvert$ exceeds a share threshold. Optional: tighten the band when $\lvert \Gamma \rvert$ is large. This step exists to trade gamma when it is there and to avoid paying stock bid/ask on every tick when it is not.
6. **Caps.** Cap the convert notional by issue size and by ADV of the stock hedge. Cap residual $\lvert \Delta \rvert$ and $\lvert \Gamma \rvert$ at book limits. This step exists so a small issue or a tight borrow does not become a position that cannot be exited or re-hedged.
7. **Blotter.** Emit bond and stock intents. Round stock to lot size; residual shares go to a cash/stock bucket. Do not route live orders. This step exists to keep the research contract off the venue.
8. **Hold and exit.** Hold 6–12 months from issuance, or exit if cheapness is gone, the bond is called, or credit limits breach. This step exists because the identity does not say when $\chi$ closes, and a call or credit event ends the option-plus-floor split you sized.

## 6. Execution protocol

- Default fill: next market snapshot after the model is frozen. Do not use the same print that just moved $S$ to recompute $\Delta$ and then fill at that print.
- Locate stock **before** buying the convert. Credit deterioration can crush the bond while the short stock rallies — size the book so that a gap in either leg does not breach limits.
- Recompute $\Delta$ daily (or on a $\Gamma$-scaled band). Hedge to $h_{\mathrm{tgt}}$ only when the share gap exceeds the band; otherwise leave $h$ unchanged.
- If the stock is halted, flatten or freeze the hedge; do not interpolate a delta through the halt and pretend the overlay still cancels.

## 7. Data contract

Required, point-in-time, timestamped $\le t-\varepsilon$ before the fill:

- Convertible dirty/clean price, accrued, conversion ratio $C$, call/put/takeout schedule
- Issuer common price, borrow availability and fee, lot size, ADV
- Treasury curve and issuer credit curve (or CDS) used by the model
- Dividend forecast dated $\le t-\varepsilon$
- Financing (repo or prime-broker) on the bond and on the short stock

Look-ahead that invalidates a historical blotter: a CDS print after $t-\varepsilon$, a dividend cut announced after $t-\varepsilon$, a revised call schedule, or using the fill-time stock print as the delta input. Dirty versus clean must be consistent on $\chi$. Borrow flags are as-of; a locate that appears the next morning does not license yesterday’s long convert.

Not used by this spec: equity factor scores, SUE.

No restatement peeking. If the bond is called or the stock is halted, flatten; do not interpolate a delta.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| pricing model | binomial or Tsiveriotis–Fernandes | freeze the choice before the test window |
| hold from issue | 6–12 months | cheapness often largest at issue |
| hedge update | daily | plus band |
| hedge band | share threshold on $\lvert h - h_{\mathrm{tgt}} \rvert$ | caller-set |
| gamma overlay | off | on $\to$ tighten band when $\lvert \Gamma \rvert$ is large |
| residual $\Delta$, $\Gamma$ caps | required | no unhedged issuance-flip |
| delay | 1 snapshot | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.convertible_arbitrage` with:

1. `cheapness(market, model_inputs) -> float` — $\chi = P_C^{\ast} - P_C^{\mathrm{mkt}}$, no look-ahead.
2. `delta(model_inputs, S) -> float` — $\Delta = \partial V / \partial S$ from the documented model.
3. `hedge_ratio(delta, C) -> float` — $h = \Delta \times C$.
4. `blotter(n_bonds, h, prices, lot, band) -> list[OrderIntent]` — bond and stock intents, residual lot bucket, never live routing.
5. `pnl(n_bonds, Q_shr, dP_C, dS, coupons, borrow, financing, costs) -> float` — matches the P&L identity above.

Delta comes from a documented pricing model. Gamma/vega limits required. No unhedged issuance-flip. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Credit + equity gap.** The bond floor collapses while the short stock rallies (2008).
- **Model $\Delta$ error.** Wrong vol, wrong credit, or a discrete call and the hedge is the wrong size.
- **Crowding / cheapening.** The convert can get cheaper after you buy it; $\chi$ is not a clock.
- **Borrow recall.** Losing the short turns a hedged book into a long-credit, long-equity residual.

## 11. Acceptance tests

- Flat $\Delta$: $V$ independent of $S$ $\Rightarrow$ $h = 0$, no stock intent.
- Linear option: $V = \Delta_0 S$ with constant $\Delta_0$ $\Rightarrow$ $h = \Delta_0 C$ exactly.
- Permuting $S$ after the model freeze must not change the $t-\varepsilon$ delta.
- If borrow is missing, the blotter emits no convert buy.
- Adding linear costs $\tau$ weakly decreases P&L.
- After a banded rebalance, $\lvert h - h_{\mathrm{tgt}} \rvert$ is at or below the share threshold.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
