---
rank: 87
slug: fx-momentum-carry-combo
title: "FX Momentum and Carry Combo"
asset_class: "foreign exchange"
style: "minimum-variance blend of two FX styles"
horizon: "Monthly combination of monthly sleeves"
instruments: "FX spot; FX forwards (typically 1m); G10 and liquid EM pairs"
---

# 087. FX Momentum and Carry Combo

| Field | Value |
|---|---|
| Popularity rank (this kit) | 87 of 101 |
| Why it sits here | Standard two-sleeve overlay: trend plus carry. Paper uses historical covariance of the two strategy returns to set weights. |
| Aliases | carry–trend mix, min-var FX overlay |
| Asset class | foreign exchange |
| Style | minimum-variance blend of two FX styles |
| Typical horizon | Monthly combination of monthly sleeves |
| Instruments | FX spot; FX forwards (typically 1m); G10 and liquid EM pairs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Combine the dual-MA / HP momentum sleeve (`052`) with the carry sleeve (`006` or `027`). One simple rule: minimum-variance weights from the $2\times 2$ sample covariance of sleeve returns.

You are betting that a variance-minimizing mix of two already-built FX styles is a better overlay than either sleeve alone, without forecasting which sleeve will win next month. The mix is at the **sleeve** level: you scale two fully formed books. You are shrinking toward the quieter, less-correlated sleeve. Equal weight $1/2,1/2$ is the robust fallback when the $2\times 2$ sample is junk.

You are not blending $D_i$ with an MA sign into a per-pair “combo score.” That mash is a different strategy and is out of this file. You are not adding a third sleeve. You are not using an expanding full-sample covariance that includes the hold. You are not mixing a delay-0 momentum sleeve with delay-1 carry: that inflates $\rho$ and the backtest.

Typical users are FX overlay desks that already run trend and carry and want a documented mixer. Horizon is monthly combination of monthly sleeves. Thirty-six monthly points on two correlated styles is a noisy $2\times 2$; weights swing. Joint crash: both sleeves lose in a risk-off unwind, and min-var does not hedge that. Delay: one month after both sleeves are known.

## 2. First principles

Let $R_1(t_s)$ be the historical return of a fully invested momentum sleeve and $R_2(t_s)$ the historical return of a fully invested carry sleeve, on the same calendar, **ending before** the mix is applied. A convex combination

$$
R = w_1 R_1 + w_2 R_2,\qquad w_1+w_2=1
$$

That mix $R$ is the overlay return. $w_1+w_2=1$ is a fully invested mix of two sleeves, not a third risk budget. If the inner sleeves already have gross one, the mix’s pair-level gross can exceed one when both sleeves are long the same name. That pile-up is a risk, not a rounding error.

The same mix has variance

$$
\mathrm{Var}(R) = w_1^2\sigma_1^2 + w_2^2\sigma_2^2 + 2 w_1 w_2 \sigma_1\sigma_2\rho
$$

This is the two-asset variance identity. $\rho$ is the correlation of *sleeve* returns, not of raw spots. Minimize that variance in $(w_1,w_2)$. The two-asset minimum-variance portfolio (no short constraint yet) is the usual closed form below. You are not forecasting which sleeve will win. You are shrinking the mix toward the quieter, less-correlated sleeve.

Equal weight $w_1=w_2=1/2$ is the robust fallback when the $2\times 2$ sample is junk. A singular covariance (identical sleeves, or a zero denominator) must not invert; it must fall back.

That is the whole strategy. Everything below is the sample moments, the clip to $[0,1]$, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $R_1,R_2$ | sleeve returns (momentum, carry) on the mix bar |
| $\sigma_1^2,\sigma_2^2$ | sample variances |
| $\rho$ | sample correlation |
| $w_1,w_2$ | sleeve weights, $w_1+w_2=1$ |
| $W$ | trailing window for $(\sigma,\rho)$, months |
| $w_i^{\mathrm{pair}}$ | the inner FX weights of sleeve $s\in\{1,2\}$ |

Inner sleeves are built from `052` and `006`/`027` with their own delay-1 rules.

## 4. Mathematics

### 4.1 Sample moments

On a trailing window of sleeve returns that ends before the mix fill (default $W=36$ months):

$$
\sigma_1^2 = \mathrm{Var}(R_1),\qquad \sigma_2^2 = \mathrm{Var}(R_2),\qquad \rho = \mathrm{Corr}(R_1,R_2)
$$

Use the same frequency as the sleeves (monthly). Do not mix daily momentum P&L with monthly carry P&L in one covariance without resampling. Moments that include the hold month peek at the mixed P&L you are about to book. Expanding full-sample covariance from 2000 through $t_{\mathrm{end}}$ is look-ahead for every earlier mix date.

### 4.2 Minimum-variance mix

Minimize $\mathrm{Var}(R)$ subject to $w_1+w_2=1$:

$$
w_1 = \frac{\sigma_2^2 - \sigma_1\sigma_2\rho}{\sigma_1^2+\sigma_2^2-2\sigma_1\sigma_2\rho}
$$

This is the closed-form weight on the momentum sleeve. It rises when carry is noisier or when correlation makes carry a worse diversifier. It is not a forecast of next month’s winner. If $\rho=0$ and $\sigma_2=2\sigma_1$, this formula gives $w_1=4/5$, which is an acceptance test.

$$
w_2 = \frac{\sigma_1^2 - \sigma_1\sigma_2\rho}{\sigma_1^2+\sigma_2^2-2\sigma_1\sigma_2\rho}
$$

The carry weight is the complement in the unconstrained problem. If a long-only mix is required, clip each weight to $[0,1]$ and renormalize so they still sum to $1$. Otherwise a small short sleeve is allowed. If the denominator is $0$ (identical sleeves), fall back to $1/2,1/2$.

Clipping a raw $w_1<0$ to $0$ and setting $w_2=1$ is the long-only default. Document clip on or off; silent clip changes the book.

### 4.3 Book construction

Build each sleeve as a fully invested FX book (its own $\sum\lvert w^{\mathrm{pair}}\rvert=1$, or its own dollar-neutral HML). Then

$$
w^{\mathrm{book}} = w_1\, w^{(1)} + w_2\, w^{(2)}
$$

This is the pair-level blend of already-computed inner weights. Do not re-rank pairs on a blended $D$+MA score in this spec. Two long-JPY sleeves become a large JPY bet unless you net and optionally rescale to a vol or gross cap. That rescale is optional and must be documented; it is not hidden in $\gamma$ of an inner sleeve.

### 4.4 Holding-period P&L

$$
\mathrm{P\&L} = w_1\,\mathrm{P\&L}_1 + w_2\,\mathrm{P\&L}_2 - \mathrm{extra\ mix\ costs}
$$

Each $\mathrm{P\&L}_s$ is the forward P&L identity of that sleeve (`052` and `006`/`027`). Extra mix costs are only costs that appear because you netted or rebalanced the blend, not a second copy of inner spreads. Report Sharpe of the mixed return and the two sleeve weights over time. Store equal-weight mix P&L next to min-var; do not silently switch to equal weight when min-var looks bad after the fact.

## 5. Step-by-step algorithm

1. **Sleeves.** Run `052` (or the dual-MA without HP, if the caller disables HP) and `006` or `027`. Freeze their delay-1 books. This step exists so the mixer does not rebuild inner signals with a different delay.
2. **History.** Collect non-overlapping monthly sleeve returns ending at $t_2$. This step exists because overlapping daily P&L in a monthly covariance double-counts.
3. **Moments.** $\sigma_1,\sigma_2,\rho$ on $W=36$ months (60 allowed). This step exists to estimate the $2\times 2$ without the hold month.
4. **Mix.** Closed-form $w_1,w_2$. Clip if long-only. Fallback $1/2$ on singular covariance. This step exists to avoid inverting a junk matrix.
5. **Map.** Linear blend of pair weights. Gross may exceed $1$ if both sleeves are long the same name; optionally rescale the book to a vol or gross cap. This step exists so pile-up is visible and optional to cap.
6. **Blotter.** One net intent per pair. Never live routing. This step exists so two sleeves do not emit two opposing forwards on the same pair.
7. **Re-estimate.** Monthly. This step exists so last year’s $2\times 2$ is not reused forever — and so you do not re-estimate through the hold.
8. **Diagnostic.** Store equal-weight mix P&L next to min-var; do not silently switch. This step exists so a noisy $2\times 2$ cannot hide behind a cherry-picked mixer.

## 6. Execution protocol

- Estimate $\sigma,\rho$ on a trailing window (36–60 months). No expanding full-sample covariance that includes the hold. If you do $X$ = fit the $2\times 2$ through $t+1$, the mix peeked.
- Clip to $[0,1]$ if a long-only mix is required; otherwise allow a small short sleeve.
- Inner execution (fixings, CIP) is inherited from the sleeve specs. A delay-0 inner sleeve plus delay-1 mix is still look-ahead in the inner book.

## 7. Data contract

Required, point-in-time:

- Everything `052` and `006`/`027` need
- A stored history of **sleeve** returns (not raw spots) for the $2\times 2$

Not used by this spec: a third sleeve, equity factors, a per-pair “combo score.”

If you do $X$ = compute covariance from raw pair spots instead of sleeve P&L, you are mixing a different object. If you do $X$ = align a delay-0 momentum P&L with delay-1 carry P&L, $\rho$ is inflated. If you do $X$ = rebuild historical sleeve returns after a WM restatement, the mix at $t_2$ was not live. Inner look-ahead rules still apply; the mixer cannot wash them out.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback $W$ | 36 months | 60 allowed |
| re-estimate | monthly | |
| clip $[0,1]$ | on | long-only mix |
| fallback | equal weight | singular $2\times 2$ |
| carry sleeve | `006` | `027` optional |
| delay | 1 month | after both sleeves are known |

## 9. Agent implementation contract

Build a Python module `strategies.fx_momentum_carry_combo` with:

1. `sleeve_returns(mom_pnl, carry_pnl) -> tuple[pd.Series, pd.Series]` — aligned, no look-ahead.
2. `minvar_weights(R1, R2, clip=True) -> tuple[float, float]` — closed form; sums to $1$ to `1e-8`.
3. `blend(w1, w2, w_mom, w_carry) -> pd.Series` — pair-level mix.
4. `blotter(blend, forwards, I) -> list[OrderIntent]` — never live routing.
5. `pnl(w1, w2, pnl1, pnl2, costs) -> float` — $w_1\mathrm{P\&L}_1+w_2\mathrm{P\&L}_2-\mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Noisy $2\times 2$.** Thirty-six monthly points, two correlated FX styles; weights swing.
- **Joint crash.** Carry and trend both lose in a risk-off unwind; min-var does not hedge that.
- **Sleeve definition leak.** Mixing a delay-0 momentum sleeve with delay-1 carry inflates $\rho$ and the backtest.
- **Gross pile-up.** Two long-JPY sleeves do not become a small JPY bet unless you net.

## 11. Acceptance tests

- $\rho=0$, $\sigma_2=2\sigma_1$ → $w_1=4/5$, $w_2=1/5$ before clip.
- Identical series $R_1=R_2$ → fallback $1/2,1/2$ (or any weights summing to 1 with identical P&L).
- Permuting sleeve returns after $t_2$ must not change $(w_1,w_2)$ at $t_2$.
- Clip on: a raw $w_1<0$ becomes $0$ and $w_2=1$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
