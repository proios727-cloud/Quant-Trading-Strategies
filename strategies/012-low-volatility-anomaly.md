---
rank: 12
slug: low-volatility-anomaly
title: "Low-Volatility Anomaly"
asset_class: "equities"
style: "defensive / low-risk"
horizon: "Vol estimated on 6m (126d) to 1y (252d). Hold a similar window. No skip period."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 012. Low-Volatility Anomaly

| Field | Value |
|---|---|
| Popularity rank (this kit) | 12 of 101 |
| Why it sits here | Huge ETF and institutional AUM in min-vol / low-vol. The long-short form is the research identity; long-only min-vol is the practitioner overlay. |
| Aliases | min-vol, low-risk anomaly |
| Asset class | equities |
| Style | defensive / low-risk |
| Typical horizon | Vol estimated on 6m (126d) to 1y (252d). Hold a similar window. No skip period. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Past low-volatility stocks outperform past high-volatility stocks on a risk-adjusted (and often raw) basis — opposite of a naive risk–return story. Rank $\sigma_i$ **ascending**. Long the quiet names, short the noisy names. There is no skip month.

You are betting that trailing quietness is underpaid and trailing noisiness is overpaid, in the equity cross-section. You are not running a minimum-variance optimizer, not levering a low-beta book to $\beta=1$ (that is betting-against-beta, a different construction), and not sorting on implied vol. The sort key is trailing realized $\sigma_i$ from adjusted prices.

You are also not importing momentum’s one-month skip. Low-vol wants the most recent month in the variance estimate; skipping it is a different signal. Typical user: a defensive equity sleeve, a min-vol ETF process, or a long-short “anomaly” book next to value and momentum. Horizon intuition: estimate vol on 6–12 months of daily (or monthly) returns, hold on a similar clock, rebalance monthly. The edge is slow. Daily-resorting $\sigma$ mostly re-ranks noise.

What you must not do: invert the sort. Long high-vol / short low-vol is the opposite trade and the most common implementation bug. If you rank descending and still call the book min-vol, the backtest is not this spec.

## 2. First principles

A name’s trailing variance is the sample second moment of its returns. On a lookback of $T$ bars with mean return $R_i^{\mathrm{mean}}$:

$$
\sigma_i^2 = \frac{1}{T-1}\sum_{t=1}^{T}\bigl(R_i(t)-R_i^{\mathrm{mean}}\bigr)^2
$$

This is ordinary sample variance on a window that **ends before** the fill. $t=1$ is the most recent completed bar — included, not skipped. The $T-1$ denominator is the usual unbiased divisor; it is not a trading rule. If the window includes the holding period, $\sigma_i$ is look-ahead. If prices are unadjusted, splits look like high vol and dump the name into the short leg by accident.

$t=1$ is the most recent completed bar in the window; the window **ends before** the fill. No skip: $t=1$ is included.

Naive compensation says $\mathbb{E}[R_i]$ rises with $\sigma_i$. The low-volatility identity is the opposite ranking on a risk-adjusted (and often raw) basis:

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} / \sigma_i \bigm| \sigma_i\bigr] \ \text{is decreasing in }\sigma_i
$$

Quiet names have *higher* expected return per unit of their own vol — and often higher raw return as well, which is the puzzle. This is an empirical ranking statement, not a CAPM identity. You implement it by sorting $\sigma_i$ **ascending**, not by running a constrained optimizer. Conditioning on realized $\sigma$ estimated in-sample on the hold would be look-ahead; the $\sigma$ here is trailing, known at the sort.

So the trade ranks $\sigma_i$ ascending, longs the bottom decile (low vol), and shorts the top decile (high vol). You are not targeting a minimum-variance optimizer. You are sorting on trailing $\sigma_i$.

Betting-against-beta (leverage a low-beta book to market $\beta=1$) is a **related but different** construction. This spec does not use betas or leverage-to-equalize.

That is the whole strategy. Everything below is how to estimate $\sigma_i$, how to turn the rank into dollars, and how not to invert the sort.

### Worked intuition

Three names, 252 daily returns already in hand, window ended yesterday. QuietCo has $\sigma=10\%$ ann., MidCo $20\%$, WildCo $40\%$. Rank ascending: long QuietCo, short WildCo in a three-name “decile” toy; MidCo is flat. There is no skip: yesterday’s return sits inside those three sigmas. If WildCo’s last month was a crash, that *raises* $\sigma$ and keeps it on the short side — the opposite of momentum’s skip, which would have thrown that month out. If you accidentally rank descending, you buy WildCo and the file’s fixture tests must fail.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price |
| $R_i(t)$ | simple return over the native bar (daily default) |
| $R_i^{\mathrm{mean}}$ | sample mean return on the lookback |
| $\sigma_i$ | trailing return volatility |
| $T$ | lookback length in bars (126 or 252 days) |
| $w_i$ | portfolio weight (positive = long) |
| $I$ | gross dollars |
| $D_i = I w_i$ | signed dollar holdings |
| $Q_i$ | signed share holdings |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$. Long-only min-vol means $w_i \ge 0$ on the low-vol names and $\sum_i w_i = 1$.

## 4. Mathematics

### 4.1 Trailing volatility

Use daily (or monthly) simple returns on the lookback. The mean is

$$
R_i^{\mathrm{mean}} = \frac{1}{T}\sum_{t=1}^{T} R_i(t)
$$

Ordinary sample mean on the same window as the variance. It is subtracted in $\sigma_i^2$ so a name with a steady drift is not automatically labelled high-vol. If you skip the mean and use raw second moment, a quiet compounder looks noisy. $t=1$ is included: no momentum skip.

The variance is the same formula as in price momentum’s formation variance, with **no skip**:

$$
\sigma_i^2 = \frac{1}{T-1}\sum_{t=1}^{T}\bigl(R_i(t)-R_i^{\mathrm{mean}}\bigr)^2
$$

Same algebra as momentum’s $\sigma^2$, different window: here the most recent bar is in, and the window is used *as the sort key*, not as a denominator on a return score. Drop names with $T$ incomplete or $\sigma_i=0$. A zero vol is a data bug or a halted name, not “infinitely low risk.”

Drop names with $T$ incomplete or $\sigma_i=0$.

### 4.2 Ranking and weights

Rank $\sigma_i$ **ascending**.

Dollar-neutral: long the bottom decile (low vol), short the top decile (high vol).

Long-only min-vol: hold the bottom decile only, $w_i \ge 0$, $\sum_i w_i = 1$. This is the practitioner variant, not the long-short identity.

Optional: vol-weight the long book $w_i \propto 1/\sigma_i$, then renormalize to the stated budget.

Modulus-uniform dollar-neutral, with $N_L$ longs and $N_S$ shorts:

$$
w_i = \frac{1}{2 N_L}\quad\text{on the longs},\qquad w_i = -\frac{1}{2 N_S}\quad\text{on the shorts}
$$

Half the gross in quiet names, half in noisy names, equal dollars inside each leg. The high-vol short leg is where borrow and squeeze live. If you skip the $1/2$, the book is not unit-gross dollar-neutral. Ranking *descending* with this same weight formula would buy high-vol — invert, and the fixture must fail.

Shares, ignoring lot-size until the blotter:

$$
Q_i = \frac{I w_i}{P_i(t_{\mathrm{fill}})}
$$

Dollars to shares at the fill, not at a price inside the vol window after the fill. Using a later price resizes on look-ahead. Lot rounding parks leftover in a cash bucket.

### 4.3 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark the signed book through the hold. Low-vol longs often pay dividends; high-vol shorts often have borrow fees. If you do X = ignore borrow on the noisy leg, the backtest lies about the expensive side of the identity. Costs must weakly cut P&L.

Report net return on gross $I$, net return on net (long) capital if long-only, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Half-sum of absolute weight changes, so a rotate from one quiet name to another is one-way turnover, not two. Low-vol should not turn over like momentum; if it does, the vol estimate is too short or you are resorting daily. If you do X = report Sharpe on overlapping holds as if independent, the backtest lies about sample size.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price above a minimum, ADV above a minimum. Keep delisted names until the delist date. Borrow available for any name that can be short (the high-vol leg). This step exists because the short leg is the noisy tail — exactly the names that are hard to borrow. Survivorship in high-vol names (failed tickers dropped) makes the short leg look easier than it was.
2. **Returns.** Compute $R_i(t)$ on the lookback that ends before the fill. No skip period. Including last month is deliberate: you want recent realized vol, not momentum’s skipped year.
3. **Vol.** Estimate $\sigma_i$. Drop incomplete histories and $\sigma_i=0$. Incomplete $T$ would let a 20-day IPO look “low vol.” Zero vol is not a valid long.
4. **Rank.** Sort $\sigma_i$ ascending. Long the lowest decile. For dollar-neutral, short the highest decile. Ascending is the entire anomaly. Descending is the opposite book.
5. **Size.** Equal weights, or $w \propto 1/\sigma$ on the long book. Enforce the stated budget. Without the budget identities, “min-vol” returns are a leverage choice, not a factor.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV (default $1\%$). Repair the budget after clipping; do not silently drop the high-vol shorts. High-vol names are often small; clipping only them leaves a residual-long quiet book.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** Monthly. Default fill: next close after $\sigma_i$ is known (delay-1). Filling on the last bar of the vol window uses a print that entered $\sigma_i$.

## 6. Execution protocol

- Low-vol names can be slow-moving large caps. High-vol shorts are expensive to borrow and crash-prone: you are short the noisy names, and in a melt-up they squeeze. If you do X = assume borrow is always 50 bp, the backtest lies on the short tail.
- If a high-vol name cannot be shorted, drop it and rebuild the short leg. Do not keep the low-vol longs and skip the shorts. If you do X = drop unborrowable high-vol names and leave longs, the backtest lies by reporting a dollar-neutral Sharpe on a net-long defensive book.
- Do not invert the sort. Ranking high-vol as the long side is the most common implementation bug. If you do X = sort descending and still label the sleeve min-vol, the backtest lies about which anomaly you ran.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted daily (or monthly) prices on the lookback and holding windows
- ADV for liquidity filters and impact caps
- Borrow availability and fees for the high-vol short leg

Not used by this spec: book value, earnings, SUE, industry map, option IV, market beta.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = estimate $\sigma$ on a window that includes the hold, vol is look-ahead. If you do X = use option IV as $\sigma_i$, this file is no longer realized low-vol. If you do X = take borrow as of today for a 2008 high-vol name, the short leg is fiction. If you do X = drop names that later delisted, the backtest lies through survivorship — especially on the noisy tail.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback $T$ | 252 days | also 126 days |
| skip | none | do not import momentum’s $S=1$ |
| decile | 10% | low vol long / high vol short |
| rebalance | monthly | |
| long-only min-vol | off | practitioner variant |
| vol-weight longs | off | $w\propto 1/\sigma$ if on |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.low_volatility_anomaly` with:

1. `trailing_vol(prices, T) -> pd.Series` — $\sigma_i$, window ends before the fill, no skip.
2. `weights(sigma, mode, scheme) -> pd.Series` — rank **ascending**; `mode` in `{long_only, dollar_neutral}`; budget identities to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
4. `pnl(D, forward_returns, costs) -> float`.

Rank **low** vol as the long side. Inverting the sort is a bug. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Inverted sort.** Long high-vol, short low-vol is the opposite trade. If you do X = unit-test only that weights sum to zero, an inverted book still passes — rank direction must be tested explicitly.
- **Short high-vol crash.** Melt-ups squeeze the short leg. If you do X = report only long-only min-vol as if it were the long-short identity, the backtest lies about squeeze risk.
- **Value/quality correlation.** Low-vol often overlaps cheap quality; the book is not a pure vol bet. If you do X = residualize against value and still claim the raw low-vol anomaly, you have a different spec.
- **Duration.** Low-vol equities can trade like long-duration bonds when rates move. If you do X = ignore rate days in a “defensive” backtest, you miss the main non-equity shock.

## 11. Acceptance tests

- Weights satisfy the stated budget identities to `1e-8`.
- Fixture: the lowest-$\sigma$ name is long, the highest is short (dollar-neutral mode). If the fixture can pass with those signs flipped, the test is too weak and an inverted backtest can lie.
- Permuting all returns after the lookback end must not change $\sigma_i$ at the sort. If shuffled future returns change $\sigma$, the vol window includes the hold and the backtest lies.
- After ADV clipping, the high-vol short leg is never silently dropped.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
