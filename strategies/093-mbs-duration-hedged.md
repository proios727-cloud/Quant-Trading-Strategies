---
rank: 93
slug: mbs-duration-hedged
title: "MBS Duration-Hedged Trading"
asset_class: "mortgage-backed securities"
style: "long passthrough vs pay fixed on rates swaps"
horizon: "Months; hedge ratios updated as rates move"
instruments: "MBS passthroughs; 5y (or matched) interest-rate swaps"
---

# 093. MBS Duration-Hedged Trading

| Field | Value |
|---|---|
| Popularity rank (this kit) | 93 of 101 |
| Why it sits here | The dealer/money-manager MBS carry book: own passthroughs, hedge duration with swaps because of negative convexity from prepayments. |
| Aliases | MBS carry, duration-hedged passthrough, OAS overlay |
| Asset class | mortgage-backed securities |
| Style | long passthrough vs pay fixed on rates swaps |
| Typical horizon | Months; hedge ratios updated as rates move |
| Instruments | MBS passthroughs; 5y (or matched) interest-rate swaps |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Own agency (or specified) MBS passthroughs and hedge interest-rate duration with pay-fixed swaps. Prepayments make MBS price a nonincreasing, negatively convex function of the 5y swap rate: as rates drop, homeowners refinance and duration shortens when you most need it. Re-estimate the hedge as the rate path changes. OAS is an optional cheap/rich filter, not the hedge identity.

You are not running a Treasury fly (file 083) or a swap-spread package (file 084) as the core book. You are long mortgage basis versus a duration-matched swap, and you must keep re-hedging because the slope $\partial P/\partial R$ is not constant. A static Treasury-duration hedge through a rally is how negative convexity is missed.

Typical users are dealer MBS desks and money managers who can face swaps and dollar rolls. Horizon is months, with hedge ratios updated as rates move: a 50bp rally is a re-estimation event, not a reason to wait for month-end. Delay-1: slope or OAD known before the fill. Pick one hedge implementation per run (constrained regression or model OAD) and document it. Mixing them mid-month restates $N_{\mathrm{swap}}$. Freeze all inputs as of $t-\varepsilon$. OAS can tilt which pools you own; it cannot replace the duration match.

## 2. First principles

Let $P$ be the passthrough dirty price (or market value) and $R$ the 5y swap rate. A first-order duration hedge would sell swap DV01 equal to $\partial P/\partial R$. Unlike a Treasury, $P$ is **not** a smooth increasing-duration instrument: prepayments imply $P$ is nonincreasing in $R$ and the slope itself shrinks as $R$ falls (negative convexity).

A nonparametric hedge estimates $\partial P/\partial R$ **subject to** $P$ nonincreasing in $R$ (constrained regression) on a window ending at $t$. Unconstrained OLS can produce a positive slope on a noisy sample, which would say “buy swaps as rates fall” and invert the hedge. The constraint exists because of that. Swap notional is that slope times MBS market value. Sign: long MBS, **pay fixed** on the swap when the estimated derivative is negative in the usual falling-rate prepay world — implement the sign from the estimated derivative, not from a hard-coded slogan.

Alternatively, a prepayment model supplies option-adjusted duration (OAD). Match swap DV01 to OAD times market value. Both routes are duration hedges; neither is an arbitrage versus Treasuries. Residual is mortgage basis, model risk, and convexity not spanned by one swap tenor. Peeking at later prepay-model recalibrations restates OAD.

That is the whole book. Everything below is the constrained slope, the swap match, and how not to look ahead. If you skip the monotone constraint, a noisy window can invert the swap. If you skip re-estimation through a rally, negative convexity leaves you under-hedged. If you skip the swap and rank on OAS alone, you own unhedged mortgage duration and this file’s identity does not apply.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P$ | passthrough price or market value |
| $R$ | 5y (or matched) swap rate |
| $\partial P/\partial R$ | estimated rate slope (constrained) |
| $N_{\mathrm{swap}}$ | pay-fixed swap notional |
| $\mathrm{DV01}_{\mathrm{swap}}$ | dollar DV01 per unit notional |
| $\mathrm{OAD}$ | option-adjusted duration from a prepay model |
| $\mathrm{OAS}$ | option-adjusted spread (filter, not the hedge) |
| $I$ | MBS market value |
| $w_{\mathrm{MBS}}$ | long MBS weight |

## 4. Mathematics

### 4.1 Constrained slope

On a trailing window ending at $t$, estimate $\partial P/\partial R$ of passthrough price $P$ with respect to 5y swap rate $R$ **subject to** $P$ nonincreasing in $R$ (constrained regression). The hedge notional in dollars of swap DV01 is

$$
N_{\mathrm{swap}}\,\mathrm{DV01}_{\mathrm{swap}} = \frac{\partial P}{\partial R}\,I
$$

with $I$ the MBS market value. Sign: pay fixed if long MBS and $\partial P/\partial R<0$ (usual); implement the sign from the estimated derivative. Units of the slope must match $\mathrm{DV01}_{\mathrm{swap}}$ (per 1bp versus per 1.00 in rate). A window that includes post-fill $R$ restates the hedge. If the constraint binds to a flat slope, you are under-hedged into a rally; that is the negative-convexity warning, not a license to drop the constraint.

### 4.2 Model OAD alternative

A prepayment model produces option-adjusted duration. Match

$$
N_{\mathrm{swap}}\,\mathrm{DV01}_{\mathrm{swap}} = -\mathrm{OAD}\cdot I \cdot \Delta R_{\mathrm{unit}}
$$

with the usual DV01 scaling (document $\Delta R_{\mathrm{unit}}$, typically 1bp). Use the model dated $\le t$; do not peek at later prepay revisions. The minus sign is the usual long-MBS / pay-fixed layout when OAD is reported as a positive duration. Mixing OAD from Friday’s model with Monday’s $I$ is a stale hedge.

### 4.3 Optional OAS filter

OAS as a secondary cheap/rich screen: overweight cheap OAS passthroughs, still duration-hedged. OAS is not a substitute for $\partial P/\partial R$. Ranking on OAS and then skipping the swap is an unhedged mortgage-basis bet, not this spec. Screen OAS is not a fill; specified-pool payups and dollar-roll specials still hit P&L.

### 4.4 Holding-period P&L

$$
\mathrm{P\&L} = \Delta P_{\mathrm{MBS}} + \mathrm{swap}_{\mathrm{MtM}} + \mathrm{carry} - \mathrm{financing} - \mathrm{costs}
$$

Carry includes MBS coupon minus projected paydowns. Report P&L, residual DV01, prepayment surprise versus the model, and mortgage-swap basis. Objective of the swap leg is duration offset, not swap alpha. A test that maximises swap Sharpe has inverted the spec. Prepay surprise (faster than the model in a rally) is the usual leftover after a static hedge.

## 5. Step-by-step algorithm

1. **Universe.** Liquid agency passthroughs (or a specified pool). Point-in-time WAC, WAM, and factor. This step exists so a TBA screen is not mixed with a specified pool without documenting payups.
2. **Factor.** 5y swap as the default rate factor (or a matched tenor). One factor will not span the whole mortgage curve; residual is accepted and reported.
3. **Hedge.** Constrained $\partial P/\partial R$ or model OAD, window/model dated $\le t$. Pick one per run. Mixing them mid-month restates $N_{\mathrm{swap}}$.
4. **Swap.** Pay-fixed (typical) notional from 4.1 or 4.2. Sign from the derivative or from OAD, not from a slogan if the estimate flipped.
5. **Filter (optional).** OAS cheap/rich overlay, still DV01-matched. Skipping the match after the filter is an unhedged tilt.
6. **Blotter.** MBS + swap intents, round, emit. Do not route live orders. Dollar-roll financing terms belong in P&L, not as a hidden boost to $I$.
7. **Re-estimate.** As the rate path changes; negative convexity means $h$ is not constant. A monthly calendar is a minimum, not a reason to ignore a 50bp rally.
8. **Delay.** Next close after the slope/OAD is known. Delay-0 is research-only.

## 6. Execution protocol

- Default fill: next close. Delay-0 is research-only. A same-bar OAD that uses the fill-day swap print is look-ahead.
- Re-estimate the slope as the rate path changes. Include basis between MBS and swaps. The basis can gap with DV01 still “correct.”
- Do not hold a static Treasury-duration hedge through a rally; that is how negative convexity is missed. Duration shortens when you most need the pay-fixed swap to be larger, and a frozen $N_{\mathrm{swap}}$ is then too small.
- Prepay-model OAS and nonparametric slope are two implementations of the same hedge idea; pick one per run and document it. Recalibrating the prepay model after $t$ does not change the $t$ notional.

## 7. Data contract

Required, point-in-time:

- Passthrough prices, factors, coupon, WAC/WAM
- 5y (or matched) swap rate and swap DV01
- For OAD: a dated prepay-model snapshot (no later recalibration peeking)
- Optional: OAS, specified-pool payups
- Financing / dollar-roll terms

Not used by this spec: equity book value, earnings, SUE, commodity COT, VIX.

Freeze all inputs as of $t-\varepsilon$ before the fill. A prepay model recalibrated after $t$ does not change the $t$ notional. Factor files (pool factor) must be the vintage available at $t$. Dollar-roll specials are financing, not a reason to mark $I$ at a TBA screen and trade a specified pool. If WAC/WAM are missing, OAD from a generic coupon is not this pool.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| factor | 5y swap | |
| hedge | constrained monotone regression | or OAD |
| regression window | caller-set | ends at $t$ |
| OAS filter | off | secondary |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.mbs_duration_hedged` with:

1. `constrained_slope(P, R, window) -> float` — $\partial P/\partial R$ with $P$ nonincreasing in $R$, window ending at $t$.
2. `swap_notional(slope, I, dv01) -> float` — $N_{\mathrm{swap}}$ from 4.1, sign from the derivative.
3. `oad_notional(OAD, I, dv01) -> float` — 4.2 alternative.
4. `blotter(I, N_swap, lot) -> list[OrderIntent]` — MBS + pay-fixed swap, never live routing.
5. `pnl(dP_mbs, swap_mtm, carry, financing, costs) -> float` — matches 4.4.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Negative convexity.** Under-hedged in a rally: duration shortens, the pay-fixed swap is too small, and you lose on both legs’ mismatch. Re-estimation is the mitigation, not a larger static $N_{\mathrm{swap}}$ chosen after the rally.
- **Mortgage basis.** MBS versus swaps can gap with the hedge still “correct” on Treasury DV01. That gap is the carry you own and the crash you sit through.
- **Model risk.** Prepay speeds, burnout, and refi incentives are estimated. A fast-prepay surprise in a rally is the usual leftover.
- **Liquidity.** Specified pools and dollar rolls gap; a screen OAS is not a fill.
- **Look-ahead OAD.** Using a recalibrated model from $t+1$ to size the $t$ swap restates the hedge.
- **Dropping the constraint.** Unconstrained positive $\partial P/\partial R$ inverts the swap and doubles the rally loss.

## 11. Acceptance tests

- Constrained slope: on a toy path with $P$ decreasing in $R$, $\partial P/\partial R\le 0$.
- $N_{\mathrm{swap}}\mathrm{DV01}_{\mathrm{swap}}=(\partial P/\partial R)I$ to `1e-8` in slope units documented by the module.
- Permuting later swap rates and passthrough prices must not change the $t$ notional.
- A parallel rate shock on a linear (zero-prepay) toy leaves combined first-order P&L $\approx 0$.
- Adding linear costs $\tau$ weakly decreases P&L.
- Swap-leg Sharpe is not a pass criterion; residual DV01 and combined P&L are.
- Unconstrained OLS that produces $\partial P/\partial R>0$ on a decreasing toy path must not pass `constrained_slope`.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
