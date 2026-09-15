---
rank: 101
slug: alpha-combos
title: "Alpha Combos"
asset_class: "equities"
style: "meta-portfolio of alphas"
horizon: "Daily close-to-close alpha returns. Weights updated on a slow clock (weeks) or when the alpha set changes."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 101. Alpha Combos

| Field | Value |
|---|---|
| Popularity rank (this kit) | 101 of 101 |
| Why it sits here | How large quant shops combine thousands to millions of faint alphas into one book. The production end-state of this catalog. |
| Aliases | alpha combination, residualized alpha mix, meta-portfolio of alphas |
| Asset class | equities |
| Style | meta-portfolio of alphas |
| Typical horizon | Daily close-to-close alpha returns. Weights updated on a slow clock (weeks) or when the alpha set changes. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Same underlying universe (example: ~2,500 liquid US names). Each alpha is a holdings process with a daily unit-gross P&L stream. Combine those streams with weights from a specific residualization: demean and vol-scale the alpha-return matrix, strip a low-rank cross-sectional factor structure, then regress expected alpha returns on what remains. The residual of that regression, scaled back by vol, is the combo weight.

You are betting that the part of expected alpha return **not** spanned by the panel’s common modes deserves capital, even if the alpha is faint stand-alone. You are not inverting an $N\times N$ alpha covariance. You are not picking stocks directly: stock-level netting happens **after** the combo, which is the point. You are not using today’s incomplete bar inside $E_i$ or $\Lambda$ while trading today.

The $M+1$ window ends yesterday. Apply $w$ tomorrow. Weights update on a slow clock (weeks) or when the alpha set changes; intra-week stock rebalance may still follow each alpha’s native clock using **stale** $w$. Alphas that cannot be traded stand-alone still get weight if they diversify. Transaction costs are at the stock level after netting. Zero-filling a missing alpha day is forbidden: drop the day from all alphas or drop the alpha. Searching $M$ or $d$ on the combo’s test Sharpe is the same leak as putting today inside $E_i$: the mix has already seen the returns it is supposed to predict.

## 2. First principles

There are $N$ alphas (here $N$ is the number of **alphas**, not stocks) and $M+1$ dated returns $R_{is}$, with $s=1$ the most recent complete day. A naive mean-variance combo would invert $\mathrm{Cov}(R)$, which is unusable when $N$ is huge. Instead, treat the panel as a factor model in **alpha space**:

$$
R_{is} = \mu_i + \sigma_i \sum_{k} \Lambda_{ik} f_{ks} + \sigma_i \eta_{is}
$$

The left-hand side is the unit-gross daily return of alpha $i$ on day $s$, already complete. The common modes $f_{ks}$ are not macro factors; they are whatever the alpha-return panel itself shares (crowding, overnight, a common industry tilt). $\sigma_i$ scales alpha $i$ so faint and loud streams are comparable before residualization. This writing is the motivation for the recipe below, not a second estimator you run on the side.

The recipe below builds a concrete $\Lambda$ by serial demeaning, vol-normalising, dropping one time column, then cross-sectionally demeaning and dropping one more column. Expected alpha returns $E_i$ (a short moving average of $R_{is}$) are vol-scaled and residualized onto that $\Lambda$ **without intercept, unit weights**. The residual $\varepsilon_i$ is the part of expected return that is **not** spanned by the panel’s common modes. Combo weights are that residual shrunk by $\sigma_i$ and scaled to unit gross:

$$
w_i = \eta\,\varepsilon_i / \sigma_i
$$

Alphas that look like the common modes get $\varepsilon_i \approx 0$ and receive little weight. Alphas that diversify them keep $\varepsilon_i$ and get capital even if they are faint stand-alone. Dividing by $\sigma_i$ maps the residual back from vol-scaled space into return space so that a noisy alpha is not automatically large in dollars. $\eta$ only enforces unit gross; it is not a risk-aversion parameter you tune on the test set.

Each alpha already maps to stock holdings; the combo holdings are the $w$-weighted sum of those holdings, then renormalized to the stock-level budget. That netting is where capacity and costs live. A combo that looks good on alpha-level $R_{is}$ and then pays stock-level spread on the residual names is the book you will actually trade.

That is the whole strategy. Everything below is the 11-step construction, the out-of-sample clock, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | alphas (not stocks) |
| $s = 1,\ldots,M+1$ | dates; $s=1$ most recent complete day |
| $R_{is}$ | realized unit-gross return of alpha $i$ on day $s$ |
| $X_{is}$ | serially demeaned $R_{is}$ |
| $\sigma_i^2$ | sample variance of $X_{i\cdot}$ |
| $Y_{is}$ | $X_{is}/\sigma_i$ |
| $\Lambda_{is}$ | cross-sectionally demeaned $Y_{is}$ (factorized panel) |
| $E_i$ | expected alpha return ( $d$-day average of $R_{is}$ ) |
| $\tilde E_i$ | $E_i/\sigma_i$ |
| $\varepsilon_i$ | residual of $\tilde E$ on $\Lambda$, no intercept, unit weights |
| $w_i$ | combo weight on alpha $i$ |
| $\eta$ | scale so $\sum_i \lvert w_i \rvert = 1$ |
| $q_{ik}$ | stock-$k$ holdings of alpha $i$ on unit gross |
| $Q_k$ | combo stock holdings after netting |

## 4. Mathematics

Procedure, as specified here.

### 4.1 Panel

Time series $R_{is}$, $s=1,\ldots,M+1$. The $M+1$ window ends yesterday. Apply $w$ tomorrow. Today’s incomplete bar is not a column. If an alpha is missing a day, drop that day from **all** alphas for the window, or drop the alpha; do not zero-fill $R_{is}$. Calendars must align across alphas on the same stock universe.

### 4.2 Serial demean

Subtract each alpha’s own time-series mean:

$$
X_{is} = R_{is} - \frac{1}{M+1}\sum_{s=1}^{M+1} R_{is}
$$

The mean uses only the $M+1$ complete days in the window. Serial demeaning is per alpha, not a cross-sectional subtract. It removes a level so that later vol-scaling is about variation, not about which alpha printed a higher mean because of a one-off. Winsorization of $R_{is}$ is off by default; if you add it, document it before this step.

### 4.3 Sample variances

The panel variance used for scaling is

$$
\sigma_i^2 = \frac{1}{M}\sum_{s=1}^{M+1} X_{is}^2
$$

The divisor is $M$, matching $M+1$ demeaned observations. Normalization of $\sigma_i$ will cancel in the final $w$ only up to $\eta$; still divide by $\sigma_i$ as written. If $\sigma_i = 0$, drop alpha $i$ and restart from this step. A zero-vol alpha is a constant stream; it is not a diversifier you can safely keep.

### 4.4 Vol-scale

Divide by that standard deviation:

$$
Y_{is} = X_{is} / \sigma_i
$$

After this step, each remaining alpha has unit sample variance in the window (up to the $M$ versus $M+1$ convention). That is what lets a faint alpha compete with a loud one in the residualization. Using a different $\sigma_i$ for $Y$ than for $\tilde E$ later is a specification bug.

### 4.5 Drop the last time column

Keep the first $M$ columns of $Y$ (discard $s = M+1$ after $Y$ is built). This is part of the factorization, not a look-ahead filter. The dropped column was still used to form $\sigma_i$ and $X$; it is discarded so the subsequent factor matrix is not square-degenerate in the usual $N \gg M$ case. Do not drop a random column; drop $s=M+1$ as written.

### 4.6 Cross-sectional demean

Subtract the equal-weight cross-section of $Y$ on each date:

$$
\Lambda_{is} = Y_{is} - \frac{1}{N}\sum_j Y_{js}
$$

This is a demean **across alphas** on each remaining date, not across stocks. It strips the equal-weight mode of the alpha panel. If $N=1$, the subtract is zero and $\Lambda$ follows $Y$. Unit weights here match the “no intercept, unit weights” regression later; value-weighting alphas at this step is a different recipe.

### 4.7 Drop one factor column

Keep the first $M-1$ columns of $\Lambda$. If all alphas are the same trade, $\Lambda$ is degenerate — drop redundant columns or alphas. The extra drop is again a rank control, not a claim that the last day was contaminated. After this step $\Lambda$ is $N \times (M-1)$.

### 4.8 Expected alpha returns

$E_i$, e.g. a $d$-day moving average of realized alpha returns ($d$ need not equal $M$):

$$
E_i = \frac{1}{d}\sum_{s=1}^{d} R_{is}
$$

$s=1,\ldots,d$ are the most recent $d$ complete days, all $\le$ yesterday. Using $s=0$ (today) inside $E_i$ while trading today is forbidden. $d$ is frozen before the test; searching $d$ on combo Sharpe in the test window is look-ahead.

Vol-scale that forecast with the same $\sigma_i$:

$$
\tilde E_i = E_i / \sigma_i
$$

Same $\sigma_i$ as in §4.3. The forecast is now in the same units as the rows of $\Lambda$. If alpha $i$ was dropped for $\sigma_i=0$, it has no $\tilde E_i$.

### 4.9 Residualization

Residuals $\varepsilon$ of the regression of $\tilde E$ on $\Lambda$ **without intercept, unit weights**. In matrix form, $\Lambda$ is $N \times (M-1)$ and

$$
\varepsilon = \tilde E - \Lambda\bigl(\Lambda^{\top}\Lambda\bigr)^{+} \Lambda^{\top} \tilde E
$$

where $(\cdot)^{+}$ is a pseudoinverse if $\Lambda^{\top}\Lambda$ is rank-deficient. Do not invert an $N\times N$ alpha covariance (that is a different, usually worse, recipe). The residual is the part of $\tilde E$ orthogonal to the columns of $\Lambda$ under unit weights. Alphas whose expected return sits in the span of the panel’s common modes are shrunk toward zero here on purpose.

### 4.10 Alpha weights

Map the residual back into return space by dividing by $\sigma_i$:

$$
w_i = \eta\,\varepsilon_i / \sigma_i
$$

Without $\eta$ this is a signed score. Dividing by $\sigma_i$ down-weights noisy alphas in dollar space. Sign follows $\varepsilon_i$: a negative residual is a short weight on that alpha’s holdings, which can net against others at the stock level.

### 4.11 Unit gross

Choose $\eta$ so that

$$
\sum_i \lvert w_i \rvert = 1
$$

This is unit gross on **alphas**, before stock netting. $\eta>0$ preserves signs. After dropping alphas, recompute $\eta$. Tolerance in tests is $10^{-8}$.

### 4.12 Stock-level netting

If alpha $i$ holds $q_{ik}$ dollars in stock $k$ on unit gross, combo holdings are

$$
Q_k = \gamma \sum_i w_i q_{ik}
$$

with $\gamma$ resetting $\sum_k \lvert Q_k \rvert$ to the stock-level budget $I$. Transaction costs are at the **stock** level after this netting. Two alphas with opposite $q_{\cdot k}$ and equal $w$ cancel on that name before $\gamma$. ADV-cap names after $Q_k$ is formed; then renormalize to $I$ and do not drop only the shorts. $q_{ik}$ is point-in-time for the same decision clock as $w$.

### 4.13 Combo P&L

Combo P&L is $\sum_i w_i$ times alpha $i$ unit P&L after stock-level netting and costs:

$$
\mathrm{P\&L} = \sum_i w_i R_{i}^{\mathrm{fwd}} - \mathrm{costs}_{\mathrm{stock}}
$$

$R_{i}^{\mathrm{fwd}}$ is the next day’s unit-gross alpha return, out of sample relative to the window that produced $w$. Stock-level costs are the real costs; alpha-level costs double-count what netting already removed. Report incremental Sharpe versus equal-weight alphas. Shuffling time for $E$ versus $\Lambda$ must not use future $R$.

## 5. Step-by-step algorithm

1. **Store.** Daily alpha returns (P&L of each alpha book on unit gross) on the same stock universe, aligned calendars. This step exists so $N$ means alphas, not stocks, and so a missing calendar cannot be zero-filled.
2. **Window.** Take $R_{is}$ for $s=1,\ldots,M+1$ ending yesterday. Do not include today’s incomplete bar. This step exists to keep $w$ strictly out of sample versus the fill.
3. **Steps 1–11.** Serial demean $\to$ $\sigma_i$ $\to$ $Y$ $\to$ drop one time column $\to$ cross-sectional demean $\to$ drop one more column $\to$ $E_i$ $\to$ $\tilde E_i$ $\to$ residualize $\to$ $w_i = \eta\varepsilon_i/\sigma_i$ $\to$ $\sum \lvert w_i \rvert = 1$. This step exists to implement the factor-in-alpha-space recipe without an $N\times N$ invert.
4. **Winsorization.** Of $R_{is}$ if used (not — if you add it, document). This step exists so an undocumented clip cannot masquerade as the listed residualization.
5. **Map to stocks.** $Q_k = \gamma \sum_i w_i q_{ik}$, then ADV-cap names. After clipping, renormalize to $I$; do not drop only the short names. This step exists because costs and capacity live at the stock level after netting.
6. **Blotter.** Stock intents from $\Delta Q$, lot-rounded, residual cash bucket. Never live routing. This step exists to keep the research contract off the venue.
7. **Clock.** Update $w$ on a slow clock (weeks) or when the alpha set changes. Intra-week stock rebalance may still follow each alpha’s native clock, using **stale** $w$. This step exists so daily $R_{is}$ noise does not re-optimize the mix every close.
8. **Flat alphas.** Alphas that cannot be traded stand-alone still get weight if they diversify. This step exists so the residualization’s point — faint diversifiers — is not deleted by a stand-alone Sharpe filter.

## 6. Execution protocol

- Run the 11 steps out of sample (the $M+1$ window ends yesterday). Apply $w$ tomorrow.
- Alphas that cannot be traded stand-alone still get weight if they diversify. Transaction costs are at the **stock** level after netting, which is the point of the combo.
- Default fill: next close after $w$ is known. Shuffling time for $E$ versus $\Lambda$ must not use future $R$.
- If an alpha is missing a day, drop that day from all alphas or drop the alpha; do not zero-fill.

## 7. Data contract

Required, aligned calendars, no look-ahead:

- Position snapshots or return streams per alpha ($R_{is}$ on unit gross)
- Same stock universe for every alpha (example: ~2,500 liquid US names)
- Point-in-time $q_{ik}$ if you net at stock level (required for live costs)
- ADV for stock-level caps
- Borrow for any name that can be net short after combo

Look-ahead that invalidates a historical blotter: including today’s incomplete $R_{i,s=0}$ in $E_i$ or $\Lambda$, zero-filling a missing alpha day, using a later $q_{ik}$ snapshot, or selecting $d$ and $M$ on test-window combo Sharpe. An $N\times N$ covariance invert is out of contract even if it “looks like” a combo.

Not used by this spec: a full $N\times N$ alpha covariance invert.

If an alpha is missing a day, drop that day from **all** alphas for the window, or drop the alpha; do not zero-fill $R_{is}$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $M$ | caller-set | panel width is $M+1$ days |
| $d$ | caller-set | $d$ need not equal $M$ |
| alpha universe | same stocks | example ~2,500 liquid US |
| winsorization of $R_{is}$ | off | if you add it, document |
| $w$ clock | weeks, or when the alpha set changes | slower than daily $R_{is}$ |
| delay | 1 day | window ends yesterday; trade tomorrow |

## 9. Agent implementation contract

Build a Python module `strategies.alpha_combos` with:

1. `combine_alpha_returns(R, E) -> w` implementing steps 1–11.
2. Shapes: `R` is $N\times(M+1)$. Assert `sum(abs(w))==1`.
3. `stock_holdings(w, q) -> Q` — $Q_k = \gamma \sum_i w_i q_{ik}$ with $\sum \lvert Q_k \rvert = I$.
4. `blotter(Q_prev, Q, prices, lot) -> list[OrderIntent]` — stock-level netting, never live routing.
5. `pnl(w, R_fwd, stock_costs) -> float` — matches $\sum_i w_i R_i^{\mathrm{fwd}} - \mathrm{costs}_{\mathrm{stock}}$.

Do not invert an $N\times N$ alpha covariance (that is a different, usually worse, recipe). Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Overfitting millions of alphas.** Capacity and costs live at the stock level; $w$ does not see them until netting.
- **Nonstationarity.** $\Lambda$ from last $M+1$ days can be a different factor tomorrow.
- **Degenerate $\Lambda$.** If all alphas are the same trade, drop redundant columns or alphas.
- **Look-ahead in $E$.** Using $R_{i,s=0}$ (today) inside $E_i$ while trading today is forbidden.

## 11. Acceptance tests

- One alpha: $w = \pm 1$ (sign of $\varepsilon_1/\sigma_1$; with $N=1$ the cross-sectional demean is zero, so $\varepsilon$ follows $\tilde E$).
- Two identical alphas: weights split or collapse depending on demeaning — pin the expected behavior in a comment and test it.
- Shuffling time for $E$ vs $\Lambda$ must not use future $R$.
- `sum(abs(w)) == 1` to $10^{-8}$ after $\eta$.
- Stock netting: two alphas with opposite $q_{\cdot k}$ and equal $w$ $\Rightarrow$ $Q_k = 0$ on that name before $\gamma$.
- Adding linear stock-level costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
