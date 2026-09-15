---
rank: 47
slug: multifactor-portfolio
title: "Multifactor Portfolio"
asset_class: "equities"
style: "factor combination"
horizon: "Inherited from the slowest factor (value) or rebalanced on the fastest (momentum) with stale slow weights."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 047. Multifactor Portfolio

| Field | Value |
|---|---|
| Popularity rank (this kit) | 47 of 101 |
| Why it sits here | How live equity books actually run: mix value, momentum, low-vol, quality, … rather than one sort. Smart-beta default. |
| Aliases | factor combination, mixed-score book |
| Asset class | equities |
| Style | factor combination |
| Typical horizon | Inherited from the slowest factor (value) or rebalanced on the fastest (momentum) with stale slow weights. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Combine $F>1$ factor portfolios with weights $w_A$, or blend ranks into one score. Three constructions: capital split, nested sorts, rank average. They are not the same book. Standardize each factor’s sign so that high = long before mixing.

You are betting that more than one documented anomaly is worth holding at once, not that mixing creates a new identity. The combo inherits every look-ahead sin of its components. You are not claiming nested momentum-then-value equals value-then-momentum, and you are not claiming capital split equals rank average.

You are also not fitting $w_A$ on in-sample factor-return covariance without calling that a small-sample overlay ([`026-statistical-arbitrage-optimization.md`](026-statistical-arbitrage-optimization.md) on $F$ series). Typical user: a smart-beta or quant equity process that already has value, momentum, and low-vol sleeves. Horizon intuition: document the clock — slowest factor (value’s 1–6m), fastest (momentum’s 1m) with stale slow weights, or a union. An undefined rebalance is not a book.

If you mix B/P (high good) with vol (high bad) without flipping vol, the combo is a high-vol bet and the backtest lies about “multifactor.”

## 2. First principles

Each factor $A=1,\ldots,F$ assigns a raw number $f_{Ai}$ to name $i$ (B/P, 12-1 return, $-\sigma$, SUE, …). A signed score is that number after flipping so that **larger means buy**:

$$
\tilde f_{Ai} = s_A\, f_{Ai}, \qquad s_A \in \{+1,-1\}
$$

Sign discipline is the whole first step. $s_A=+1$ for value and momentum; $s_A=-1$ for volatility so that *low* vol becomes a high signed score. Mixing unsigned vol with value longs noisy names. The combo module must refuse unsigned inputs; silent $s_A=+1$ on every factor is the classic bug.

$s_A=+1$ for value and momentum; $s_A=-1$ for volatility. Mixing B/P (high good) with vol (high bad) without flipping vol is a classic bug.

Three ways to build one book from $F$ signed factors:

**A.** Allocate capital across already-built factor portfolios. **B.** Nest sorts (intersection of deciles). **C.** Average cross-sectional ranks, then sort once.

They are not interchangeable. A can hold a name that is a momentum winner and a value loser (offsetting sleeves). B can require high on the first sort then high on the second (order matters). C scores every name on every factor then sorts once. Pick `method` and do not mix labels.

Rank average is the unique equal-weight combination that minimizes the sum of squared Euclidean distances from the combo rank-vector to the factor rank-vectors. That is why it is the default single-score blend.

That is the whole strategy. Everything below is the three constructions, sign discipline, and how not to overfit $w_A$.

### Worked intuition

Two names, two factors. CheapSlow has high B/P (value long) and low 12-1 (momentum short). FastRich has low B/P and high 12-1. Capital split with $w_A=1/2$ holds both sleeves: CheapSlow is long value and short momentum, net maybe small; FastRich is the opposite. Rank average demeans each factor’s ranks and averages: if the two ranks are exact opposites, $s_i\approx 0$ and both names can fall out of the combo deciles — cancellation. Nested momentum-then-value keeps only names that are *both* winners and cheap, which may be neither of these two. Same inputs, three books.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe |
| $A = 1,\ldots,F$ | factors |
| $f_{Ai}$ | raw factor value for name $i$ |
| $s_A$ | sign so that high = long |
| $w_A$ | capital weight on factor portfolio $A$; $w_A>0$, $\sum_A w_A=1$ |
| $I_A = w_A I$ | dollars allocated to factor $A$ |
| $\sigma_A$ | trailing vol of factor-portfolio returns (for risk-budget $w_A$) |
| $\mathrm{rank}(f_{Ai})$ | cross-sectional rank of factor $A$ |
| $s_{Ai}$ | demeaned rank of factor $A$ on name $i$ |
| $s_i$ | combined score |
| $w_i$ | name-level portfolio weight |
| $I$ | gross dollars |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$. Long-only means $w_i \ge 0$ and $\sum_i w_i = 1$.

## 4. Mathematics

### 4.1 Capital split (method A)

Factor portfolios are already built by their own specs. Allocate

$$
I_A = w_A I, \qquad w_A > 0, \quad \sum_A w_A = 1
$$

Dollars to sleeve $A$. Uniform $w_A=1/F$ is the default. Inverse-vol / inverse-var use trailing $\sigma_A$ of the *already-built* factor books, estimated on a window that ends before the fill. Mean-variance on the $F\times F$ factor-return covariance is the optimizer file on $F$ assets — document it; in-sample MV on a handful of series is a small-sample trap.

Uniform: $w_A = 1/F$. Inverse-vol: $w_A \propto 1/\sigma_A$. Inverse-var: $w_A \propto 1/\sigma_A^2$. Or mean-variance on the $F\times F$ factor-return covariance (then the overlay is [`026-statistical-arbitrage-optimization.md`](026-statistical-arbitrage-optimization.md) on $F$ assets).

The name-level weight is the sum of the component books:

$$
w_i = \sum_A w_A\, w_{i}^{(A)}
$$

Linear combination of already-budgeted sleeves. A name long in value and short in momentum nets. Re-normalize if you need $\sum_i \lvert w_i\rvert=1$ exactly after the sum. If a component silently dropped its shorts, the combo inherits residual beta.

Re-normalize if you need $\sum_i \lvert w_i\rvert=1$ exactly after the sum.

### 4.2 Nested sorts (method B)

Example: take top/bottom momentum quintiles, then split each by value (or the reverse). These two nests are **not** the same portfolio. Document the order. Intersection of “high on every factor” is a different object again (a sequential filter, not a nest).

Nest order is load-bearing. Momentum-then-value keeps extreme momentum names and then tilts them by value; value-then-momentum does the reverse. If you do X = report one nest’s returns under the other nest’s name, the backtest lies. Intersection (“must be top-decile on all $F$”) is smaller and slower; do not label it `nested` without saying so.

### 4.3 Rank average (method C)

Demeaned ranks for each factor:

$$
s_{Ai} = \mathrm{rank}(\tilde f_{Ai}) - \frac{1}{N}\sum_{j=1}^{N}\mathrm{rank}(\tilde f_{Aj})
$$

Cross-sectional rank of the *signed* factor, then demean so each factor’s rank vector is zero-sum. Demeaning makes equal-weight averaging well-defined. Ranking unsigned vol here would treat high vol as high rank — sign first. Ties: break by a designated factor.

Equal-weight combination:

$$
s_i = \frac{1}{F}\sum_{A=1}^{F} s_{Ai}
$$

Average of demeaned ranks. This is the unique equal-weight combo that minimizes the sum of squared Euclidean distances from $s$ to the factor-rank vectors. Weighted $\sum_A \omega_A s_{Ai}$ is allowed but heavier — document $\omega_A$. Opposite-sign duplicate factors cancel ($s_i\approx 0$ up to ties).

Ties: break by a designated factor. Averaging $s_{Ai}$ minimizes the sum of squared Euclidean distances from $s$ to the factor-rank vectors. Weighted average $\sum_A \omega_A s_{Ai}$ or other metrics (Manhattan) are allowed but heavier.

Then sort on $s_i$ as in any single-factor spec: long top decile, short bottom, or long-only top.

### 4.4 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

with $D_i = I w_i$. Combined-book P&L, not the average of sleeve Sharpes. Costs on the combo can be less than the sum of sleeve costs if offsets reduce turnover — or more, if you rebalance to the fastest clock. If you do X = average three sleeve backtests instead of marking $w_i$, you miss netting.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

One-way turnover of the *combined* weights. Horizon: inherited from the slowest factor (value) or rebalanced on the fastest (momentum) with stale slow weights. Document which. If you do X = refresh value daily because momentum rebalances daily, you are not running stale-slow; you are running a different, faster value book.

Horizon: inherited from the slowest factor (value) or rebalanced on the fastest (momentum) with stale slow weights. Document which.

## 5. Step-by-step algorithm

1. **Universe.** Intersection of the component factors’ universes after liquidity filters. Keep delisted names until the delist date. Intersection exists so a name missing book cannot sneak in via momentum-only. Survivorship still applies to every component.
2. **Signed scores.** Each factor exposes `signed_score(i)` with documented $s_A$. Refuse unsigned inputs. This step exists because vol’s sign is the usual silent bug.
3. **Method.** Pick `capital`, `nested`, or `rank_avg`. The three are different books; this step exists so the caller cannot leave `method` implicit.
4. **Combine.** A: build each factor book, allocate $I_A=w_A I$, sum weights. B: apply nested sorts in the documented order. C: demean ranks, average, then one sort. Each branch must still use only data $\le$ `asof`.
5. **Budget.** Enforce long-only or dollar-neutral on the **combined** $w_i$. Component budgets do not automatically imply a combo budget after netting and caps.
6. **Caps.** ADV clip, then repair the budget; do not silently drop shorts. Combo tails can still be illiquid even if each sleeve was capped.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** Document whether the clock is the slow factor, the fast factor, or a union. An undocumented clock makes $w_{t}$ vs $w_{t-1}$ undefined.

## 6. Execution protocol

- Standardize each factor’s sign so that high = long **before** any average or nest. If you do X = average raw $\sigma$ with B/P, the backtest lies by buying high-vol as if it were value.
- Delay-1 on the fastest factor in the mix. A stale slow factor is allowed; a future slow factor is not. If you do X = use next month’s book equity in a momentum-dated rebalance, the backtest lies.
- If a name cannot be shorted, drop it from the combined book and rebuild. If you do X = drop shorts only in the momentum sleeve and keep value shorts, neutrality of the combo is an accident.

## 7. Data contract

Required, point-in-time: **all inputs of the component factors**, each under that factor’s own data contract.

Typical union when mixing value, momentum, and low-vol:

- Split- and dividend-adjusted prices (momentum, low-vol, and fills)
- Point-in-time book equity if value is in the mix
- ADV and borrow

Include SUE and announcement timestamps **only** if earnings momentum is a component. Include Fama–French factors **only** if residual momentum is a component.

No restatement peeking. Delisted names stay until the delist date.

If you do X = take value’s restated book and momentum’s delay-0 close in one combo, both component sins survive. If you do X = omit borrow because “the combo is long-only” while `mode` is dollar-neutral, the short legs are fiction. If you do X = use a factor that was not in the list at $t$, look-ahead membership.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| `method` | `rank_avg` | `{capital, nested, rank_avg}` |
| factor list | caller-set | each with $s_A$ |
| $w_A$ | $1/F$ | capital method only |
| nest order | required if nested | two orders are different books |
| decile | 10% | after the combo score |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.multifactor_portfolio` with:

1. `signed_score(factor_id, panel, asof) -> pd.Series` — documented sign; combo refuses unsigned inputs.
2. `combine(scores, method, weights=None, nest_order=None) -> pd.Series` — name-level $s_i$ or $w_i$.
3. `weights(score, mode) -> pd.Series` — budget identities to `1e-8`.
4. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Hidden concentration.** Value and quality often buy the same names. If you do X = report $F$ as diversification without looking at name overlap, the backtest lies about risk.
- **Overfit $w_A$.** In-sample factor-cov MV on $F$ series is a small-sample trap. If you do X = retune $w_A$ every month on the same $F$ returns you trade, the backtest lies.
- **Different optimal holds.** Averaging a 1-month momentum book with a 6-month value book without a clock rule produces an undefined rebalance. If you do X = that, turnover and Sharpe are not well-defined.
- **Sign error.** Unflipped low-vol turns the combo into a high-vol bet. If you do X = skip $s_A$, the backtest lies about multifactor.

## 11. Acceptance tests

- Two identical factors → combo equals one factor (rank-avg and capital split).
- Opposite-sign duplicate → cancellation in rank-avg ($s_i=0$ up to ties).
- Flipping $s_A$ on vol must change who is long. If flipping vol’s sign leaves the book unchanged, signs were ignored and a multifactor backtest lies.
- Nested momentum-then-value $\neq$ value-then-momentum on a fixture where the two ranks disagree.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
