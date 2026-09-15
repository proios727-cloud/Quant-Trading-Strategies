---
rank: 100
slug: fundamental-macro-momentum
title: "Fundamental Macro Momentum"
asset_class: "global macro"
style: "cross-asset ranking on macro state variables"
horizon: "3–6 month hold"
instruments: "country equity indexes, FX, government bonds — typically via futures or ETFs"
---

# 100. Fundamental Macro Momentum

| Field | Value |
|---|---|
| Popularity rank (this kit) | 100 of 101 |
| Why it sits here | Systematic global macro: rank country equity indexes (and other assets) on growth, trade, policy, and risk-sentiment trends (Brooks-style). |
| Aliases | fundamental momentum, Brooks-style macro ranks, state-variable momentum |
| Asset class | global macro |
| Style | cross-asset ranking on macro state variables |
| Typical horizon | 3–6 month hold |
| Instruments | country equity indexes, FX, government bonds — typically via futures or ETFs |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Incoming macro is summarized in four state variables: business cycle, international trade, monetary policy, and risk sentiment. Rank assets by how much that incoming macro favours them. Long the top decile, short the bottom; blend asset-class books equally. Hold 3–6 months.

You are betting that 1-year changes in forecasts and policy, dated when they were public, forecast the cross-section of country equity indexes, FX, and government bonds. You are not trading price momentum of the asset itself, except that the risk-sentiment sleeve is defined as a 1-year equity excess return. You are not using revised GDP or a later CPI print to rebuild a historical $Z$. You are not substituting illiquid cash bonds for liquid futures or ETFs and calling it the same book.

Each state is a 1-year change on a vintage clock. Signs are frozen before the test window: stronger growth forecasts typically favour that country’s equities; falling short rates may favour that country’s bonds — document the table, do not flip it when the sample looks better. Implementation is futures or ETFs. Fill is the next liquid close after $Z$ is known. Delay-0 on the forecast print date is research-only. A Consensus Economics or IMF vintage stamped after $t-\varepsilon$ is as illegal as a restated GDP print; the survey date is the clock, not the forecast’s horizon year.

## 2. First principles

An asset $j$ in asset class $A$ (country equity index, FX, government bond) has a next-horizon excess return $R_j$. A small set of slow state variables $Z$ is assumed to forecast the cross-section:

$$
\mathbb{E}[R_j \mid Z] = \alpha_j + \beta_j^{\top} Z
$$

This is a motivation, not a live regression you re-estimate every month on the holding sample. You do not need to estimate $\beta_j$ live. The operational proxy is: measure a 1-year **change** in each state, rank names on a blend of those changes, and hold the high ranks versus the low ranks. Equal 50/50 where a state is itself two series. All inputs are vintages dated $\le t-\varepsilon$.

**Business cycle** for country $c$: one-year change in the real GDP growth forecast and in the CPI inflation forecast, equally mixed:

$$
Z_c^{\mathrm{bc}} = \tfrac12 \Delta_{1\mathrm{y}} g_c^{\mathrm{GDP}} + \tfrac12 \Delta_{1\mathrm{y}} \pi_c^{\mathrm{CPI}}
$$

$g_c^{\mathrm{GDP}}$ and $\pi_c^{\mathrm{CPI}}$ are **forecasts**, not realized GDP or CPI. $\Delta_{1\mathrm{y}}$ compares the forecast vintage today with the forecast vintage one year ago, both as they were published then. A later GDP revision must not change a historical $Z_c^{\mathrm{bc}}$. The 50/50 mix is a default; a different mix is a different state and must be frozen before the test.

**Trade:** one-year change in the spot FX versus an export-weighted basket $B_c$:

$$
Z_c^{\mathrm{tr}} = \Delta_{1\mathrm{y}} \ln\bigl(S_c / S_{B_c}\bigr)
$$

$S_c / S_{B_c}$ is spot versus a basket whose weights are dated $\le t-\varepsilon$. Rebuilding the basket with later trade weights is look-ahead. Sign the rank so that the sleeve owns the side the documented table calls favoured (for example, a stronger currency versus the export basket as a positive for that country’s assets, or the reverse — freeze it). Equity-index futures already embed FX; double-counting $Z^{\mathrm{tr}}$ against an unhedged equity future is a specification bug you must document or avoid.

**Policy:** one-year change in the short rate:

$$
Z_c^{\mathrm{pol}} = \Delta_{1\mathrm{y}} r_c^{\mathrm{short}}
$$

$r_c^{\mathrm{short}}$ is the policy or short market rate known at $t-\varepsilon$, not a later revised average. The sign of this rank can flip when the reaction function changes; that is a risk, not a license to re-sign inside the test window. For bonds, falling short rates are often the favoured side; for equities the favoured side may differ. Freeze the sign table per asset class.

**Risk sentiment:** one-year equity excess return for that country (or the global risk sleeve, as documented):

$$
Z_c^{\mathrm{rs}} = R_{c,[t-1\mathrm{y},t]}^{\mathrm{ex}}
$$

This sleeve is price momentum in equity excess returns, used as a macro state, not as the whole strategy. The window ends at $t$, using only closes already known. A global risk sleeve, if used, must be the same object for every country on that date and dated $\le t-\varepsilon$.

All $\Delta_{1\mathrm{y}}$ and returns use vintages dated $\le t-\varepsilon$. Point-in-time forecasts only (no revised GDP).

Rank country indexes on a blend of the four. A simple aggregator is the average of cross-sectional ranks:

$$
\bar\rho_c = \tfrac14 \sum_{k\in\{\mathrm{bc,tr,pol,rs}\}} \mathrm{rank}(Z_c^{k})
$$

Each $\mathrm{rank}(Z_c^{k})$ is a cross-sectional rank on that date, after the documented sign so that “high” means “favoured.” Nested sorts are allowed if documented; they are **not** the same portfolio as average ranks. Missing $Z$ for a country drops the name; do not fill with zeros. Long top decile, short bottom. Repeat inside each asset class. Combine asset-class sub-portfolios with equal weights. Hold 3–6 months.

That is the whole strategy. Everything below is how to sign each $Z$ so that “high” means “favoured,” how to implement with futures/ETFs, and how not to peek at revisions.

## 3. Notation

| Symbol | Definition |
|---|---|
| $c$ | country (or FX pair / bond future in that sleeve) |
| $A$ | asset class: equities, FX, government bonds |
| $Z_c^{\mathrm{bc}}, Z_c^{\mathrm{tr}}, Z_c^{\mathrm{pol}}, Z_c^{\mathrm{rs}}$ | four state variables |
| $\Delta_{1\mathrm{y}}$ | 1-year change, point-in-time |
| $g_c^{\mathrm{GDP}}, \pi_c^{\mathrm{CPI}}$ | real GDP growth and CPI inflation **forecasts** |
| $S_c / S_{B_c}$ | spot vs export-weighted basket |
| $r_c^{\mathrm{short}}$ | short rate |
| $\bar\rho_c$ | average rank across the four states |
| $w^{(A)}$ | weights inside asset class $A$, dollar-neutral |
| $I_A$ | gross dollars in sleeve $A$; default $I_A = I/3$ |

## 4. Mathematics

### 4.1 State construction

Example state construction (1-year changes, equal 50/50 where two series):

- Business cycle: 1y change in real GDP growth forecast and CPI inflation forecast
- Trade: 1y change in spot FX vs an export-weighted basket
- Policy: 1y change in short rates
- Risk sentiment: 1y equity excess return

Those are the four formulas in §2. Document the **sign** of each rank so that a high $\bar\rho_c$ is the side the sleeve should own (e.g. stronger growth forecasts $\to$ long that country’s equity index; the policy sleeve may rank **falling** short rates as favoured for bonds — freeze the sign table before the test window). A vintage timestamp that is missing is a drop, not an interpolation from a later print.

### 4.2 Ranking and legs

Rank country indexes on a blend of the four. Default aggregator: average ranks $\bar\rho_c$. Alternative: nested sorts (these two are **not** the same; pick one). Long top decile, short bottom, equal-weight or vol-weight inside legs. Dollar-neutrality inside sleeve $A$ is

$$
\sum_c w_c^{(A)} = 0
$$

This is a sleeve-level identity, not a global identity across asset classes. Countries that appear in more than one sleeve are separate contracts (equity future vs FX vs bond future), not one net $w_c$.

and the sleeve is unit gross:

$$
\sum_c \lvert w_c^{(A)} \rvert = 1
$$

After ADV / open-interest caps, repair these two identities; do not drop only the short names. Equal-weight versus vol-weight inside legs is a documented choice.

### 4.3 Asset-class mix

Combine asset-class sub-portfolios with equal weights. Default three sleeves (equities, FX, bonds), each with gross

$$
I_A = I/3
$$

A missing sleeve (no liquid bond future) is not silently reallocated unless you document a two-sleeve mix. $I$ is the book’s total gross.

Country dollars are the sum of the sleeves:

$$
D_c = \sum_A I_A w_c^{(A)}
$$

Only sleeves that contain $c$ contribute. Hold 3–6 months. Rebalance monthly or at the holding horizon; if monthly with a 3-month hold, average three overlapping books. Overlapping books are an average of weights, not a stretch of one formation window.

### 4.4 Holding-period P&L

Implement with futures or ETFs, not illiquid cash bonds. Let $R_c^{\mathrm{fwd}}$ be the excess return of the implementing contract (futures roll included):

$$
\mathrm{P\&L} = \sum_c D_c R_c^{\mathrm{fwd}} - \mathrm{costs}
$$

$R_c^{\mathrm{fwd}}$ is from fill to next rebalance, including roll. Costs include commissions, spread, and roll slippage. Report net return on gross $I$, Sharpe on non-overlapping holding-period returns, and turnover. Delay-1: $Z$ known at $t-\varepsilon$ trades the next liquid close.

## 5. Step-by-step algorithm

1. **Universe.** Liquid country equity index futures or ETFs, liquid FX, liquid government-bond futures. Drop names with missing $Z$ after a documented lag. This step exists so the book cannot hide in cash bonds or in a country with a hole in the forecast tape.
2. **Vintages.** Pull 1-year changes in forecasts, FX, short rates, and equity excess returns with timestamps $\le t-\varepsilon$. No revised GDP. This step exists so a later statistical office print cannot rewrite yesterday’s rank.
3. **States.** Build $Z^{\mathrm{bc}}, Z^{\mathrm{tr}}, Z^{\mathrm{pol}}, Z^{\mathrm{rs}}$ with the 50/50 mix where specified. This step exists to turn four slow clocks into four comparable series before ranking.
4. **Blend.** Average ranks (default) or nested sorts. Document the aggregator. This step exists because the two aggregators are different portfolios; a silent mix is a bug.
5. **Legs.** Long top decile, short bottom, inside each asset class. Dollar-neutral per sleeve. This step exists so a global risk-on book cannot masquerade as three independent sleeves.
6. **Mix.** Equal asset-class gross $I/3$. Cap by contract ADV / open interest. This step exists so one liquid equity index cannot eat the whole $I$.
7. **Blotter.** Futures/ETF intents, lot-rounded. Never live routing. This step exists to keep the research contract off the venue.
8. **Hold.** 3–6 months. Rebalance monthly or at horizon; overlapping books allowed. This step exists because the states are slow; daily rebalancing is a different, noisier book.

## 6. Execution protocol

- Point-in-time forecasts only (no revised GDP). Rebalance monthly or at the holding horizon.
- Use futures/ETFs, not illiquid cash bonds, for implementation.
- Fill at the next liquid close after $Z$ is known. Delay-0 on the forecast print date is research-only.
- Freeze the sign table for each $Z$ per asset class before the test window.

## 7. Data contract

Required, point-in-time, vintage-dated:

- Real GDP growth **forecasts** and CPI inflation **forecasts** (1y change)
- Spot FX and an export-weighted basket definition dated $\le t-\varepsilon$
- Short rates
- Country equity excess returns for the risk-sentiment sleeve
- Futures/ETF prices, rolls, and open interest / ADV
- Trading calendars

Look-ahead that invalidates a historical blotter: replacing a GDP forecast with a later revision, rebuilding export weights with later trade data, using a short-rate series that was revised, or filling missing $Z$ with zeros. Forecast print dates are the vintage clock; a survey timestamped after $t-\varepsilon$ is out.

Not used by this spec: single-name stock ranks, tweet text, convertibles.

No revision peeking: a later GDP print must not change a historical $Z^{\mathrm{bc}}$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| states | four as above | 50/50 inside business cycle |
| aggregator | average ranks | nested sorts allowed if documented |
| legs | top vs bottom decile | dollar-neutral per sleeve |
| asset-class mix | equal | $I/3$ each |
| hold | 3–6 months | monthly rebalance with overlap allowed |
| implementation | futures/ETFs | not illiquid cash bonds |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.fundamental_macro_momentum` with:

1. `states(vintages) -> pd.DataFrame` — $Z^{\mathrm{bc}}, Z^{\mathrm{tr}}, Z^{\mathrm{pol}}, Z^{\mathrm{rs}}$, no revision peeking.
2. `ranks(states, aggregator) -> pd.Series` — $\bar\rho_c$ or nested-sort key.
3. `weights(ranks, I_A) -> pd.Series` — dollar-neutral $w^{(A)}$, $\sum w = 0$ and $\sum \lvert w \rvert = 1$ to `1e-8`.
4. `blend(weights_by_class, I) -> pd.Series` — equal asset-class mix.
5. `blotter(D, prices, lot) -> list[OrderIntent]` — futures/ETF intents, never live routing.
6. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_c R_c^{\mathrm{fwd}} - \mathrm{costs}$.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Forecast revisions.** Using final GDP instead of vintages is a different, invalid book.
- **Policy regime shifts.** The sign of $Z^{\mathrm{pol}}$ can flip when the reaction function changes.
- **FX overlay interaction.** Equity-index futures already embed FX; double-counting $Z^{\mathrm{tr}}$ is a specification bug.
- **Macro momentum crashes.** Crowded growth-up books unwind together.

## 11. Acceptance tests

- Two countries, opposite $\bar\rho$, one asset class $\to$ equal-dollar opposite futures positions, $\sum D = 0$.
- Three asset classes, equal mix $\to$ each sleeve gross $I/3$ to $10^{-8}$ before lot rounding.
- Replacing a GDP forecast with a later revision must not change the historical $t-\varepsilon$ rank.
- Missing $Z$ for a country $\Rightarrow$ drop, do not fill with zeros.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
