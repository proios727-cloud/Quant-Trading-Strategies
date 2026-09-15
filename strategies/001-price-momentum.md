---
rank: 1
slug: price-momentum
title: "Price Momentum"
asset_class: "equities"
style: "cross-sectional momentum"
horizon: "Formation 12m skip 1m; hold 1m (academic). Practitioners also run 3–12m formation on daily bars."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 001. Price Momentum

| Field | Value |
|---|---|
| Popularity rank (this kit) | 1 of 101 |
| Why it sits here | The most-cited equity factor after the market itself. Default first sleeve in every multi-factor book. |
| Aliases | cross-sectional momentum, 12-1 momentum |
| Asset class | equities |
| Style | cross-sectional momentum |
| Typical horizon | Formation 12m skip 1m; hold 1m (academic). Practitioners also run 3–12m formation on daily bars. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Buy recent winners, sell recent losers. Future returns are positively correlated with past returns over intermediate horizons, after skipping the most recent month. That skip is load-bearing: without it the sort mixes one-month reversal into the momentum signal.

You are betting that a name which already outperformed its peers over the prior year, excluding last month, will keep outperforming for one more holding month. You are not betting that yesterday’s tape continues, that last month’s losers bounce, or that a single stock’s chart has a “trend line.” The object is a **cross-section**: winners versus losers inside a liquid universe, not a timer on one ticker.

You are also not betting on book-to-price, earnings surprises, or trailing volatility. Those are other files. Price momentum uses only split- and dividend-adjusted prices on a formation window. If a name is cheap, high-quality, or quiet, that is incidental overlap, not the signal.

Typical user: a quant equity desk or a smart-beta sleeve that already runs value and wants a second, faster factor. Academic books rebalance monthly on 12-1 ranks. Practitioner books sometimes form on 3–12 months of daily bars and still hold about a month. Horizon intuition: formation is slow (a year of path), the skip is one month of microstructure, and the hold is short because the edge decays before costs if you stretch it.

If you skip the skip, daily-rebalance a yearly score, or fill on the same close you ranked, the backtest is a different — usually better-looking — object than a tradable 12-1 book.

## 2. First principles

Index months so that $t=0$ is the most recent completed month and $t$ increases into the past. The simple return of month $t$ is then the ratio of that month’s close to the previous (older) close:

$$
R_i(t) = \frac{P_i(t)}{P_i(t+1)} - 1
$$

That identity is just “this month’s close over last month’s close, minus one,” with the time index running backward. $P_i(t)$ is already split- and dividend-adjusted, so a 2-for-1 does not look like a −50% month. If you used unadjusted prices, every split would pollute the formation rank. The formula does not yet skip anything; it only defines the monthly tape you will later window.

A one-month reversal / microstructure effect sits in the most recent month. Skip it by starting formation at month $S$ (default $S=1$), not at $t=0$.

Over an intermediate window of length $T$ (default $T=12$), names that rose tend to keep rising. Write the holding-period expected return as a continuation of that skipped formation return:

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} \bigm| R_i^{\mathrm{cum}}\bigr] \approx \lambda\, R_i^{\mathrm{cum}}, \qquad \lambda > 0
$$

This is the empirical claim, not an identity. $\lambda>0$ says continuation: high formation return, high next-month expected return. If $\lambda$ were negative you would be writing reversal and the long-short book would flip. The conditioning variable is the skipped cumulative return, not last month and not the holding-period return itself — using $R_i^{\mathrm{fwd}}$ on the right-hand side would be look-ahead.

$R_i^{\mathrm{cum}}$ is the return from $S+T$ months ago to $S$ months ago. $\lambda>0$ is the continuation. You are not betting that last month continues (that is reversal). You are betting that the prior year, excluding last month, continues for one more month.

That is the whole strategy. Everything below is how to measure $R_i^{\mathrm{cum}}$ (or a mean / risk-adjusted twin), how to turn the rank into dollars, and how not to look ahead.

### Worked intuition

Three names, month-end closes already adjusted. Skip $S=1$, formation $T=12$, so the score uses $P(1)/P(13)-1$. Suppose A goes 80 → 100 over that window (+25%), B goes 100 → 90 (−10%), C goes 50 → 55 (+10%). Rank A, then C, then B. In a three-name “decile” toy, long A and short B; C is the middle and is flat. Month 0’s return never enters those three numbers. If A’s last month was −8% because of a lagging print, that print is in the skip, not in the score — which is the point of $S=1$.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe after liquidity filters |
| $P_i(t)$ | split- and dividend-adjusted price; $t=0$ is the most recent month-end |
| $R_i(t)$ | simple return of month $t$, looking backward in $t$ |
| $S$ | skip months (usually 1) |
| $T$ | formation months (usually 12) |
| $H$ | holding months (usually 1) |
| $R_i^{\mathrm{cum}}$ | formation cumulative simple return on $[S+T,\,S]$ |
| $R_i^{\mathrm{mean}}$ | mean monthly return on the formation window |
| $\sigma_i^2$ | sample variance of monthly formation returns |
| $R_i^{\mathrm{risk.adj}}$ | $R_i^{\mathrm{mean}} / \sigma_i$ |
| $w_i$ | portfolio weight (positive = long) |
| $I$ | gross dollars; $I = I_L + I_S$ in the dollar-neutral book |
| $D_i = I w_i$ | signed dollar holdings |
| $Q_i$ | signed share holdings |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$. Long-only means $w_i \ge 0$ and $\sum_i w_i = 1$.

## 4. Mathematics

### 4.1 Formation cumulative return

Skip the most recent $S$ months. Formation length is $T$. The cumulative simple return on that window is

$$
R_i^{\mathrm{cum}} = \frac{P_i(S)}{P_i(S+T)} - 1
$$

This is a two-point ratio, not a sum of monthly returns. $P_i(S)$ is the close $S$ months ago (just outside the skip); $P_i(S+T)$ is the close one formation window further back. Default $S=1$, $T=12$ is twelve-minus-one: you measure the year that ended last month, not the year that ended today. If either price is missing, drop the name — do not stitch a stale quote, or the rank is fiction.

Default: $S=1$, $T=12$ (twelve-minus-one). Log returns $\ln\bigl(P_i(S)/P_i(S+T)\bigr)$ are interchangeable when $\lvert R_i^{\mathrm{cum}}\rvert$ is not huge; this spec uses simple returns as written above.

### 4.2 Mean and risk-adjusted sorts

The mean monthly formation return is

$$
R_i^{\mathrm{mean}} = \frac{1}{T}\sum_{t=S}^{S+T-1} R_i(t)
$$

This averages the $T$ skipped-window monthly returns instead of using only the two end prices. A name that grinded up steadily can rank like a name that spiked once and sat; $R^{\mathrm{cum}}$ treats those two paths as the same terminal ratio. Use the mean when you want path smoothness in the score. The sum still starts at $t=S$, so month 0 is out.

The sample variance on the same window is

$$
\sigma_i^2 = \frac{1}{T-1}\sum_{t=S}^{S+T-1}\bigl(R_i(t)-R_i^{\mathrm{mean}}\bigr)^2
$$

This is the usual unbiased sample variance on the same $T$ months that entered the mean. It is there so a later risk-adjusted score can down-weight names whose formation path was a noisy spike. If you skip this and sort only on $R^{\mathrm{cum}}$, a 3× biotech that doubled on one print looks like a quiet compounder. If $T=1$, the denominator $T-1$ is zero — that is why formation is not one month.

The risk-adjusted formation score is

$$
R_i^{\mathrm{risk.adj}} = \frac{R_i^{\mathrm{mean}}}{\sigma_i}
$$

Divide the formation mean by formation vol so a high-vol winner does not automatically dominate a steady winner. This is still a formation statistic, not a forecast of next-month vol. If $\sigma_i=0$ the ratio is undefined: drop the name rather than emitting infinity. The three sorts — cum, mean, risk-adj — are not the same portfolio.

Sort on $R_i^{\mathrm{cum}}$, $R_i^{\mathrm{mean}}$, or $R_i^{\mathrm{risk.adj}}$. The three sorts are not the same portfolio. Default sort key: $R_i^{\mathrm{cum}}$.

### 4.3 Ranking and weights

Rank the chosen score descending. Winners are the top decile. Losers are the bottom decile.

Long-only: hold the winners with $w_i \ge 0$ and $\sum_i w_i = 1$. Dollars in name $i$ are $I w_i$. Shares, ignoring lot-size until the blotter, are

$$
Q_i = \frac{I w_i}{P_i(0)}
$$

This converts a dollar weight into a share count at the month-end price used for the decision (or at the fill price once delay-1 is applied). Rounding to lots happens later; this identity is the unrounded target. If you use a later price in the denominator, you have resized on information that was not in the rank. $Q_i$ inherits the sign of $w_i$.

Dollar-neutral: long the winners, short the losers, with $\sum_i \lvert w_i\rvert = 1$ and $\sum_i w_i = 0$. Gross is $I = I_L + I_S$ with $I_L = I_S$, so $I = 2 I_L$.

Uniform long-only on $N$ held names:

$$
w_i = \frac{1}{N}
$$

Equal dollars in every winner. That is the simplest long-only book and the one academic papers usually report first. It ignores vol and ADV; noisy small names get the same dollars as quiet large names. After ADV caps you will have to repair this so the weights still sum to one.

Vol-scaled (then renormalize to the stated budget): $w_i \propto 1/\sigma_i$ or $w_i \propto 1/\sigma_i^2$.

Modulus-uniform dollar-neutral, with $N_L$ longs and $N_S$ shorts:

$$
w_i = \frac{1}{2 N_L}\quad\text{on the longs},\qquad w_i = -\frac{1}{2 N_S}\quad\text{on the shorts}
$$

Half the gross sits in the winner basket, half in the loser basket, spread equally inside each leg. If $N_L \neq N_S$ (after liquidity drops), each long is not the exact opposite of each short, but the two *legs* still have equal dollars. If you skip the $1/2$ and put $1/N_L$ on longs, the book is no longer dollar-neutral at unit gross.

### 4.4 Holding-period P&L

Hold $H=1$ month (or longer; the signal decays before costs). To build a $K$-month hold, average $K$ overlapping 1-month books rather than stretching one formation window.

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

This marks the signed dollar book through the holding-period return and then subtracts costs. Dividends belong in $R_i^{\mathrm{fwd}}$ because winners often pay them and losers sometimes cut them. If you mark with price-only returns, you silently drop income. Costs must be weakly positive; a backtest that adds a rebate as negative costs is a different claim.

Report:

- net return on gross $I$
- net return on net (long) capital if long-only
- annualized Sharpe on **non-overlapping** holding-period returns
- one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t}-w_{i,t-1}\rvert
$$

The one-half stops you from double-counting a sale on one name and a buy on another as two full turns. Overlapping $K$-month holds that are reported as if they were independent inflate Sharpe; use non-overlapping returns for the headline number. If you do X = compute Sharpe on overlapping monthly books without saying so, the backtest lies about how many independent bets you had.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price above a minimum, ADV above a minimum, exclude recent IPOs if desired. Keep delisted names until the delist date (no survivorship). Borrow must be available for any name that can be short. This step exists so the sort is a tradable cross-section, not a museum of dead tickers and unborrowable losers. If you drop names that later delist, the backtest lies by keeping only survivors.
2. **Returns.** Using only prices with timestamp $\le$ month-end $t=0$, compute $R_i(t)$ on the formation window with the backward time index above. This step exists to freeze the information set. A restated or late-arriving price after $t=0$ does not get to rewrite month $t$’s return.
3. **Score.** Compute $R_i^{\mathrm{cum}}$ with $S=1$, $T=12$ (or $R_i^{\mathrm{mean}}$ / $R_i^{\mathrm{risk.adj}}$ if selected). Drop names with missing formation prices; do not impute. Imputation manufactures ranks for names you could not have scored live. The skip is applied here, not later as a comment.
4. **Rank.** Sort descending. Long the top decile. For dollar-neutral, also short the bottom decile. Ranking is the map from a continuous score to a sparse book. If you weight all $N$ names by the raw score, you have a different, denser strategy with higher turnover.
5. **Size.** Apply a weighting scheme (equal, inverse-vol, inverse-var, or modulus-uniform). Enforce the stated budget: long-only $\sum w_i=1$, $w_i\ge 0$ or dollar-neutral $\sum w_i=0$, $\sum \lvert w_i\rvert=1$. Without the budget identities, “gross $I$” is undefined and every later P&L number is a scale artifact.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV (default $1\%$). After clipping, repair the budget; do not silently drop the short leg. This step exists because equal-weight losers are often the least liquid names. If you clip shorts and leave longs untouched, the book becomes a residual-long winner bet.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Rounding needs a cash bucket so leftover dollars do not silently vanish from P&L.
8. **Rebalance.** Monthly. For a 6-month hold, average six overlapping 1-month books. Default fill: next close after ranks are known (delay-1). Academic delay-0 close-to-close is a backtest choice, not a live book. If you fill on the same close that entered the rank, you are assuming you traded inside the print that created the signal.

## 6. Execution protocol

- Trade at the next close (or next open) after ranks are known. Live books need a delay-1 close or a next-open fill. If you do X = rank and fill on the same month-end close, the backtest lies by capturing the close-to-close move that was already in the score.
- Cap names by ADV. If a name cannot be shorted, drop it and rebuild the short leg on the remaining losers. Do not keep the longs and skip the shorts. If you do X = omit hard-to-borrow losers while keeping all winners, the backtest lies by reporting a dollar-neutral Sharpe on a net-long book.
- The 1-month skip is required. Ranks at month-end $t$ must not use month $t$ returns. If you do X = set $S=0$ and still call the book 12-1 momentum, the backtest lies by mixing reversal into the headline factor.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted daily or monthly prices covering $[S+T,\,0]$ and the holding window
- ADV for liquidity filters and impact caps
- Borrow availability and fees for any short

Not used by this spec: book value, earnings, SUE, industry map.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = use CRSP-style delisting returns only for names that remain in a current-universe file, the backtest lies through survivorship. If you do X = apply a split adjustment that was announced after $t=0$ to month $t$ ranks, the backtest lies by using a later corporate-action tape. If you do X = fill ADV from a monthly average that includes the holding month, the cap is look-ahead.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $S$ | 1 month | skip; do not set to 0 without calling the book a mix of reversal |
| $T$ | 12 months | formation |
| $H$ | 1 month | hold; overlap $K$ books for a $K$-month hold |
| sort key | $R^{\mathrm{cum}}$ | alternatives: `mean`, `risk_adj` |
| decile | 10% | winners / losers |
| weighting | equal | `{equal, inverse_vol, inverse_var}` |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.price_momentum` with:

1. `formation_score(prices, skip_months, formation_months, signal) -> pd.Series` — $R^{\mathrm{cum}}$, $R^{\mathrm{mean}}$, or $R^{\mathrm{risk.adj}}$; `signal` in `{cum, mean, risk_adj}`; no look-ahead.
2. `weights(score, mode, scheme) -> pd.Series` — `mode` in `{long_only, dollar_neutral}`; budget identities to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — shares $Q_i$, residual cash bucket, never live routing.
4. `pnl(D, forward_returns, costs) -> float` — matches $\sum D_i R_i^{\mathrm{fwd}} - \mathrm{costs}$.

`skip_months` and `formation_months` are required arguments, default 1 and 12. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Momentum crashes.** After a market rebound, recent losers bounce harder than winners; the short leg blows up. If you do X = report only long-only winner returns as if they were the dollar-neutral identity, the backtest lies about crash exposure.
- **Skip omitted.** Without $S=1$ you mix one-month reversal into the signal. If you do X = form on 12 months including last month and still label it 12-1, the backtest lies about which anomaly you tested.
- **Short-leg failure.** Losing the shorts turns a dollar-neutral sort into a residual-long winner bet. If you do X = drop unborrowable losers without rebuilding $\sum w_i=0$, the backtest lies by keeping market beta.
- **Turnover vs value.** Intermediate-horizon momentum turns over faster than value; costs eat the edge on small names. If you do X = apply a 1 bp cost to a micro-cap loser book, the backtest lies about net P&L.

## 11. Acceptance tests

- Weights satisfy the stated budget identities to `1e-8`.
- Three names, known prices, closed-form $R^{\mathrm{cum}}$ and decile membership.
- Permuting all prices after month 0 must not change the formation score at $t=0$. If you do X = let a shuffled future path change $R^{\mathrm{cum}}$, the implementation looks ahead and the backtest lies.
- Ranks at month-end $t$ must not use month $t$ returns (skip window). If month $t$ returns change the rank, the skip is broken.
- After ADV clipping, either the budget still holds or the cash bucket absorbs the residual; the short leg is never silently dropped. If you do X = clip shorts to zero and leave longs, the test must fail.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
