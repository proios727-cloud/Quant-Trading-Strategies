---
rank: 2
slug: value
title: "Value"
asset_class: "equities"
style: "cross-sectional value"
horizon: "Rebalance monthly to semi-annually. Holding 1–6 months."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 002. Value

| Field | Value |
|---|---|
| Popularity rank (this kit) | 2 of 101 |
| Why it sits here | The other canonical equity factor (book-to-price / HML). Core of every quant equity process. |
| Aliases | book-to-price, HML-style value |
| Asset class | equities |
| Style | cross-sectional value |
| Typical horizon | Rebalance monthly to semi-annually. Holding 1–6 months. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Buy high book-to-price (cheap), sell low book-to-price (expensive). B/P equals book-to-market when book and market are totals. Two live price conventions exist; they are not the same portfolio. Pick one and document it.

You are betting that names the market is pricing at a low multiple of accounting equity subsequently earn more than names at a high multiple. You are not forecasting next quarter’s earnings, not timing the market, and not claiming that book is “true value.” Book is a slow accounting stock; price is a fast market stock; the ratio is the sort key.

You are also not running price momentum, SUE, or min-vol. A cheap name can be a recent loser, a recent winner, or neither. Value’s typical user is a quant equity or smart-beta process that wants a slow complementary sleeve next to momentum. Horizon intuition: book updates at most quarterly, price updates daily, and the edge is slow — rebalance monthly to semi-annually. Daily-rebalancing B/P mostly trades denominator noise.

What you are not betting: that the gap closes this month, that negative-book names are infinitely cheap, or that a 10-K restated years later was known at the sort. Filing lag is load-bearing. If you use restated book or mix current-price and lagged-price conventions silently, the backtest is a different factor than the one you named.

## 2. First principles

Market price is book equity times a multiple. Per share:

$$
P_i = B_i\, m_i
$$

This is a definition of the multiple, not a pricing model. $B_i$ is the accounting book per share that was public at the sort; $m_i$ is whatever the market is paying for that book. If $B_i$ is stale and $P_i$ is live, $m_i$ mixes two dates. That mix is allowed only when you document `price_convention=current`. The identity does not say $m_i$ is fair; it says price is book times a number you can invert.

$B_i$ is book equity per share known at the sort. $m_i$ is the multiple the market is paying for that book. Invert:

$$
v_i = \frac{B_i}{P_i} = \frac{1}{m_i}
$$

High $v_i$ is a low multiple: cheap relative to accounting equity. Low $v_i$ is expensive. Ranking on $v_i$ is the same order as ranking on $B_i/P_i$ and the opposite order of ranking on $P_i/B_i$. If you rank on $P/B$ and still long the top decile, you have bought expensive names. The ratio is unitless only if $B$ and $P$ share a scale (both per share, or both totals).

$v_i$ is book-to-price. High $v_i$ means a low multiple: the name is cheap relative to its accounting equity. Value says that cheap names have higher subsequent returns than expensive names:

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} \bigm| v_i\bigr] \approx \alpha + \lambda\, v_i, \qquad \lambda > 0
$$

This is the empirical slope, not an accounting identity. $\lambda>0$ says cheap (high $v$) has higher expected holding-period return. $\alpha$ is a level; it does not change ranks. The claim is cross-sectional, not that every cheap name rallies. If $\lambda$ is estimated in-sample on the same $R^{\mathrm{fwd}}$ you trade, you have fitted the test, not specified a sort.

You are not forecasting earnings. You are ranking on the accounting-to-price ratio and holding the cheap side (and shorting the expensive side in the dollar-neutral book).

That is the whole strategy. Everything below is which $P_i$ to put in the denominator, how to keep $B_i$ point-in-time, and how to turn the rank into dollars.

### Worked intuition

Two names, same book date, both filings already public. Name Cheap has $B=20$ and $P=40$, so $v=0.50$. Name Rich has $B=20$ and $P=80$, so $v=0.25$. The sort longs Cheap and shorts Rich. Nothing in those two ratios says Cheap’s earnings will beat estimates; it only says the market is paying half as much per dollar of book. If Rich’s 10-K printed the day *after* the sort, you do not get to use that $B$ at the sort — even if the fiscal year ended last month. If you switch the denominator from today’s close to last year’s close, both $v$ numbers change and the ranks can flip: that is why `price_convention` is an enum, not a comment.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe after liquidity filters |
| $P_i$ | price used in the ratio (convention documented below) |
| $B_i$ | book equity per share, last reported figure available as of the sort |
| $v_i = B_i / P_i$ | book-to-price value score |
| $m_i$ | price-to-book multiple $P_i / B_i$ |
| $w_i$ | portfolio weight (positive = long) |
| $I$ | gross dollars; $I = I_L + I_S$ in the dollar-neutral book |
| $D_i = I w_i$ | signed dollar holdings |
| $Q_i$ | signed share holdings |
| $R_i^{\mathrm{fwd}}$ | simple holding-period return including dividends |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$. Long-only means $w_i \ge 0$ and $\sum_i w_i = 1$.

## 4. Mathematics

### 4.1 Value score

The baseline score is book-to-price:

$$
v_i = \frac{B_i}{P_i}
$$

Same identity as in §2, now as the implemented sort key. Missing $B_i$ or $P_i$ means drop the name, not fill with last year’s Compustat vintage. Negative $B_i$ makes $v_i$ negative: those names sort as “expensive” unless you exclude them. The spec does not force exclusion, but most HML-style books do — document it.

Allowed twins of the same identity, not different models: $\ln(B_i/P_i)$, or enterprise-value variants (EV/EBITDA and kin) if the caller documents the substitution. Default remains $B_i/P_i$.

B/P equals book-to-market when $B_i$ and $P_i$ are both totals (book equity and market cap) rather than per share. Use a consistent scale.

### 4.2 Price convention

Two conventions for $P_i$ are in wide use. They do not produce the same ranks.

- **Current-price.** $P_i$ is the last close at the rebalance. Book is still lagged to be public. The ratio mixes a stale numerator with a live denominator.
- **Lagged-price.** $P_i$ is the price contemporaneous with the book date (typically last fiscal year, lagged until the filing is public). Numerator and denominator share a date.

`price_convention` is a required enum `{current, lagged_ff}`. Mixing the two silently is a bug.

Current-price value is more “live”: a name that rallied since the filing looks more expensive. Lagged-price value is closer to Fama–French HML construction: both legs of the ratio sit at the book date, then you wait until the filing is public to trade. If you do X = compute $v$ with last year’s book and yesterday’s price, then later claim the book is Fama–French lagged, the backtest lies about which convention you ran.

### 4.3 Ranking and weights

Rank $v_i$ descending. Long the top decile (cheap). Short the bottom decile (expensive) in the dollar-neutral book, or hold the top decile only in the long-only book.

Uniform long-only on $N$ held names:

$$
w_i = \frac{1}{N}
$$

Equal dollars in every cheap name. Simple, and the usual long-only smart-beta starting point. It ignores that some cheap names are tiny and expensive to trade. After ADV caps you must renormalize so the weights still sum to one.

Modulus-uniform dollar-neutral, with $N_L$ longs and $N_S$ shorts:

$$
w_i = \frac{1}{2 N_L}\quad\text{on the longs},\qquad w_i = -\frac{1}{2 N_S}\quad\text{on the shorts}
$$

Half the gross in cheap, half in expensive. If liquidity filters thin one leg, $N_L$ and $N_S$ can differ; the *legs* still have equal dollars. Skipping the $1/2$ leaves a net-long or net-short book that is no longer the HML-style identity.

Shares, ignoring lot-size until the blotter:

$$
Q_i = \frac{I w_i}{P_i(t_{\mathrm{fill}})}
$$

Convert dollars to shares at the fill price, not at the (possibly lagged) price that sat in the B/P ratio. Using the lagged book-date price in the denominator here would size the trade off a stale quote. Lot rounding comes after; park leftover dollars in a cash bucket.

Practitioners usually exclude negative book so the high-minus-low sort is clean. This spec does not force that exclusion; if you keep negative-book names, document it.

### 4.4 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Mark the signed dollar book through the hold and subtract costs. Cheap names are often dividend payers; dropping dividends from $R^{\mathrm{fwd}}$ understates the long leg. Costs on the expensive short leg include borrow. If you do X = mark with total returns on longs and price-only on shorts, the backtest lies in your favor.

Report:

- net return on gross $I$
- net return on net (long) capital if long-only
- annualized Sharpe on **non-overlapping** holding-period returns
- one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

The one-half avoids double-counting a rotate from one cheap name into another. Value turnover is usually much lower than momentum; if your monthly value book turns over like 12-1, you are probably using current-price B/P without a dead-band. If you do X = daily-rebalance B/P, the backtest lies by treating denominator noise as alpha.

Value is slow. Do not daily-rebalance B/P without a documented reason (price noise in the denominator).

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price above a minimum, ADV above a minimum. Keep delisted names until the delist date. Borrow available for any name that can be short. This step exists so cheapness is measured among names you could actually hold. Survivorship — dropping names that later failed — makes historical cheap baskets look safer than they were.
2. **Book.** Take the last reported book equity available as of the sort timestamp. No restatements, no filing that prints after the sort. This step exists because Compustat “final” book is not what a live sorter had. If you do X = use restated book, the backtest lies.
3. **Price.** Apply the documented `price_convention`: last close, or the price aligned with the book date. This step exists because the two conventions are different portfolios. Silent mixing is a spec bug, not a robustness check.
4. **Score.** $v_i = B_i / P_i$. Drop names with missing $B_i$ or $P_i$. Optionally drop negative book. Do not impute book from market cap or from a sector median; that manufactures a value score you did not observe.
5. **Rank.** Sort $v_i$ descending. Long top decile, short bottom decile (dollar-neutral) or long top decile only. Ranking is what turns a ratio into a sparse book. Weighting all names by raw $v_i$ is a different, denser overlay.
6. **Size.** Equal or modulus-uniform weights. Enforce the stated budget. Without $\sum w=0$ and $\sum\lvert w\rvert=1$ (or the long-only analogues), reported returns are scale artifacts.
7. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV (default $1\%$). Repair the budget after clipping; do not silently drop the short leg. Cheap and expensive tails are both full of small names. Dropping only the shorts leaves residual market beta.
8. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Rebalance monthly to semi-annually. A cash bucket holds rounding residual so P&L still matches $\sum D_i R_i^{\mathrm{fwd}}$.

## 6. Execution protocol

- Low turnover relative to momentum. Trade at month-end close plus delay-1 (or next open). If you do X = fill on the same close that entered current-price $P_i$, the backtest lies by capturing the close that just changed the ratio.
- Filing lag: book dated $T$ cannot be used before its actual print date. If you do X = align book to fiscal year-end rather than print date, the backtest lies by several months of look-ahead on slow filers.
- If a name cannot be shorted, drop it and rebuild the expensive leg. Do not keep the longs and skip the shorts. If you do X = skip hard-to-borrow rich names, the backtest lies by reporting HML on a net-long cheap book.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices for the chosen price convention and the holding window
- Point-in-time book equity and shares outstanding (so per-share and total B/P match)
- Filing timestamps for the book figure actually used
- ADV for liquidity filters and impact caps
- Borrow availability and fees for any short

Optional variants, only if selected: earnings, enterprise value, EBITDA.

Not used by this spec: SUE, earnings-announcement timestamps (except as a filing clock if that is how book becomes public), industry map.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = pull “as reported” book from a database that overwrites history with restatements, the backtest lies. If you do X = use a point-in-time book but a current share count from after a split, per-share $B_i$ is wrong. If you do X = take ADV from the holding month, the liquidity filter looks ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| score | $B_i/P_i$ | $\ln(B/P)$ or EV variants allowed if documented |
| `price_convention` | required enum | `{current, lagged_ff}`; no silent mix |
| decile | 10% | cheap / expensive |
| rebalance | 1 month | `{1m, 6m}` |
| negative book | exclude | not forced, but usual |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.value` with:

1. `value_score(book, price, asof, price_convention) -> pd.Series` — $v_i$; book dated $T$ is refused if its print date is after `asof`.
2. `weights(score, mode) -> pd.Series` — `mode` in `{long_only, dollar_neutral}`; budget identities to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — shares $Q_i$, residual cash bucket, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}} - \mathrm{costs}$.

`price_convention` is required. Mixing current-price and lagged-price silently is a bug. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Long droughts.** Value drawdowns can last years; the identity does not say the gap closes this month. If you do X = stop the backtest after the first three good years, the backtest lies about holding-period pain.
- **Look-ahead on filings.** Using restated book or a 10-K that was not yet public is a different strategy. If you do X = use SEC file date plus zero lag on a close that already traded, you still may be filling before the print was in the tape.
- **Negative book and financials.** Banks and negative-equity names distort B/P. If you do X = keep negative book, long them as “cheap,” the sort is not HML-as-usually-implemented.
- **Accounting regimes.** Cross-country book is not the same object. If you do X = pool US GAAP and local IFRS without a country or sector neutralization, the backtest lies about a single “value” factor.

## 11. Acceptance tests

- Weights satisfy the stated budget identities to `1e-8`.
- Filing lag: book dated $T$ cannot be used before its actual print date. If a post-`asof` print changes $v_i$, the implementation looks ahead and the backtest lies.
- Holding `price_convention` fixed, permuting prices after the sort date must not change $v_i$ under `lagged_ff`; under `current` only the live close at the sort may change.
- After ADV clipping, the short leg is never silently dropped. If clipping zeros the expensive leg and leaves cheap longs, the test must fail.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ raises P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
