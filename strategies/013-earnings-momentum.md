---
rank: 13
slug: earnings-momentum
title: "Earnings Momentum"
asset_class: "equities"
style: "event / PEAD"
horizon: "Hold about 6 months; returns fade after that. Rebalance after each earnings print or monthly on latest SUE."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 013. Earnings Momentum

| Field | Value |
|---|---|
| Popularity rank (this kit) | 13 of 101 |
| Why it sits here | Post-earnings-announcement drift (SUE). One of the most replicated earnings anomalies. Same winner/loser geometry as price momentum, with SUE as the sort key. |
| Aliases | SUE, PEAD |
| Asset class | equities |
| Style | event / PEAD |
| Typical horizon | Hold about 6 months; returns fade after that. Rebalance after each earnings print or monthly on latest SUE. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Buy positive standardized unexpected earnings, sell negative. Same winner/loser geometry as price momentum, with SUE as the sort key. Use actual print dates, not fiscal period ends.

You are betting that the market absorbs a seasonal earnings surprise slowly, so the stock still drifts in the direction of the surprise after the print. You are not ranking on the EPS *level*, not forecasting next quarter’s print, and not trading the announcement-window jump itself (that jump is mostly in the print bar you must not fill on).

You are also not running price momentum. A high-SUE name can be a chart loser. The sort key is $(E-E')/\sigma$ from announcement timestamps $\le$ `asof`. Typical user: an event-driven or quant equity sleeve that already has prices and wants an earnings overlay. Horizon intuition: the drift is strongest in the days after the print, still there in a monthly rebalance on latest SUE, and fades after about six months. Holding a stale SUE from two quarters ago is not PEAD.

If you use fiscal period-end instead of the print date, or restated EPS after `asof`, the backtest is a look-ahead cousin of this spec, not SUE as a live sorter could have computed it.

## 2. First principles

Seasonal random-walk earnings say this quarter’s EPS is last year’s same quarter, plus a shock:

$$
E_i = E'_i + u_i
$$

$E_i$ is the latest **announced** quarterly EPS, not a consensus forecast and not a restatement that printed later. $E'_i$ is the EPS announced four quarters ago — the same fiscal quarter last year — not “calendar last year approx.” $u_i$ is the seasonal surprise. If seasonality is strong (retail, tax names), this is the right null; if it is not, $u_i$ is just a noisy difference. The identity does not say $u_i$ is unpredictable in real time; it defines the surprise you will standardize.

$E_i$ is the most recently **announced** quarterly EPS. $E'_i$ is the EPS announced four quarters ago. $u_i$ is unexpected earnings.

The shock is not in the same units across names. Scale it by the trailing standard deviation of that same seasonal surprise over the last eight quarters:

$$
\sigma_i = \mathrm{stdev}\bigl(E_i^{(q)} - E_i^{(q-4)}\bigr)_{q=1,\ldots,8}
$$

A \$0.10 surprise is huge for a \$0.20 EPS name and nothing for a \$10 name. Eight quarters of the same seasonal difference is the usual denominator. Fewer than eight → drop the name; do not emit infinite SUE. $\sigma_i=0$ (identical surprises every year) is refused for the same reason. This $\sigma$ is an EPS-unit scale, not stock-return vol.

Standardized unexpected earnings is then the $z$-score of the latest shock:

$$
\mathrm{SUE}_i = \frac{E_i - E'_i}{\sigma_i}
$$

Latest seasonal surprise in units of its own trailing scale. High SUE is a large positive surprise; low (negative) SUE is a large miss. This is the sort key. Ranking on $E_i$ itself would buy high-EPS names, which is not PEAD. Ranking on $u_i$ without $\sigma_i$ would overweight large-EPS names.

Post-earnings-announcement drift says the market absorbs $u_i$ slowly. Holding-period expected return continues the sign of SUE:

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} \bigm| \mathrm{SUE}_i\bigr] \approx \lambda\, \mathrm{SUE}_i, \qquad \lambda > 0
$$

Empirical continuation on the standardized surprise, not on last month’s return. $\lambda>0$ is the PEAD slope. The holding-period return on the right-hand side must not enter SUE. Conditioning is on prints dated $\le$ `asof`. If $\lambda$ is fit on the same $R^{\mathrm{fwd}}$ you trade, you have fitted the test.

You are not ranking on the EPS level. You are ranking on the standardized seasonal surprise, using only prints whose announcement timestamp is $\le$ the sort.

That is the whole strategy. Everything below is how to keep the four-quarter lag exact, how to refuse $\sigma_i=0$, and how to turn the rank into dollars.

### Worked intuition

Name PrintCo announces \$1.20 this quarter. Four quarters ago it announced \$1.00. The last eight seasonal differences have $\sigma=0.10$. SUE $= (1.20-1.00)/0.10 = +2.0$: a two-sigma beat, long-decile candidate. Name MissCo announces \$0.80 versus \$1.00 a year ago, same $\sigma$, SUE $=-2.0$: short-decile candidate. If PrintCo’s 10-Q was filed Tuesday after the close and you sort Monday night, that \$1.20 is not in the information set. If a later restatement changes \$1.20 to \$1.05, the live sorter never saw \$1.05 at `asof` — using it is a different, better-looking backtest.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the tradable universe after liquidity filters |
| $E_i$ | most recently announced quarterly EPS (split-adjusted) |
| $E'_i$ | EPS announced four quarters ago, not “last year approx” |
| $u_i = E_i - E'_i$ | seasonal unexpected earnings |
| $\sigma_i$ | stdev of $E^{(q)}-E^{(q-4)}$ over the last 8 quarters |
| $\mathrm{SUE}_i$ | $u_i / \sigma_i$ |
| $w_i$ | portfolio weight (positive = long) |
| $I$ | gross dollars |
| $D_i = I w_i$ | signed dollar holdings |
| $Q_i$ | signed share holdings |
| `asof` | sort timestamp; every print used must have announcement time $\le$ `asof` |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$. Long-only means $w_i \ge 0$ and $\sum_i w_i = 1$.

## 4. Mathematics

### 4.1 SUE

The sort key is

$$
\mathrm{SUE}_i = \frac{E_i - E'_i}{\sigma_i}
$$

Same identity as in §2, now as the implemented score. $E'_i$ is the $q-4$ print, not “EPS from last calendar year.” Skip names with fewer than eight quarters of history if $\sigma_i$ would be undefined. Refuse $\sigma_i=0$. A restatement of $E_i$ dated after `asof` must not enter this ratio.

The four-quarter lag is exact: $E'_i$ is the print from $q-4$, not a calendar-year approximation. Skip names with fewer than eight quarters of history if $\sigma_i$ would be undefined. Refuse $\sigma_i=0$.

### 4.2 Ranking and weights

Rank $\mathrm{SUE}_i$ descending. Dollar-neutral: long the top SUE decile, short the bottom. Long-only: hold the top decile.

Modulus-uniform dollar-neutral, with $N_L$ longs and $N_S$ shorts:

$$
w_i = \frac{1}{2 N_L}\quad\text{on the longs},\qquad w_i = -\frac{1}{2 N_S}\quad\text{on the shorts}
$$

Half the gross in beats, half in misses. Event-time books may have uneven $N_L$ and $N_S$ in a given month (earnings cluster in weeks); the *legs* still get equal dollars. Skipping the $1/2$ leaves a net-long PEAD book that is not the identity.

Shares, ignoring lot-size until the blotter:

$$
Q_i = \frac{I w_i}{P_i(t_{\mathrm{fill}})}
$$

Size in stock at the fill, which must be after `asof`. Using the pre-announcement close as both `asof` and fill captures the jump the spec is not claiming to trade. Lot rounding uses a cash bucket.

### 4.3 Holding-period P&L

PEAD is strongest in the days after the print; a monthly rebalance on latest SUE still works but is slower. Hold about 1–6 months; the drift fades after that.

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Forward returns start *after* the print is public. If $R^{\mathrm{fwd}}$ includes the announcement-bar jump, you have mixed event alpha into PEAD. Costs on the miss leg include borrow; names that just missed are often hard to short. If you do X = fill at yesterday’s close when the print hit this morning, the backtest lies by capturing the jump.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Event rebalance turns over when prints arrive; monthly rebalance turns over more slowly. Overlapping six-month holds reported as independent months inflate Sharpe. If you do X = annualize a sample of overlapping PEAD windows, the backtest lies about how many independent surprises you had.

## 5. Step-by-step algorithm

1. **Universe.** Listed names, price and ADV filters. Keep delisted names until the delist date. Borrow available for names that can be short. This step exists because missed-earnings shorts are the painful leg. Dropping later-failed names makes historical miss baskets look too kind.
2. **Prints.** For each name, take EPS prints with announcement timestamps $\le$ `asof`. Ignore fiscal period end if it differs from the print date. Watch stale earnings (no print this quarter): still use the latest eligible SUE, or drop if the print is older than a documented stale cutoff. Fiscal period-end is not when the market saw the number.
3. **SUE.** $E_i$ = latest print, $E'_i$ = print four quarters back, $\sigma_i$ from the last eight seasonal surprises. Drop names with $<8$ history or $\sigma_i=0$. Exact $q-4$, not “last year.” Infinite SUE is a bug.
4. **Rank.** Sort SUE descending. Long top decile, short bottom decile (dollar-neutral) or long top only. Ranking is the map from a z-score to a sparse book.
5. **Size.** Equal or modulus-uniform weights. Enforce the stated budget. Without the identities, reported PEAD returns are a leverage choice.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of ADV. Repair the budget; do not silently drop the short leg. Misses are often smaller names; clipping only shorts leaves residual-long beats.
7. **Blotter.** Convert to shares, round to lot size, emit intents. Do not route live orders. Cash bucket for lots.
8. **Rebalance.** After each earnings print, or monthly on latest SUE. `asof` must precede any price used for the subsequent hold. Default fill: next close (delay-1). Filling the print bar itself is delay-0 event trading, not this spec.

## 6. Execution protocol

- Use actual print dates, not fiscal period ends. If you do X = sort on period-end $T$ with EPS that printed at $T+20$, the backtest lies by about a month of look-ahead on slow filers.
- A monthly rebalance is slower than trading the days after the print; both are allowed if documented. If you do X = mix event-time fills into a monthly book without saying so, the backtest lies about implementation.
- If a name cannot be shorted, drop it and rebuild the low-SUE leg. If you do X = skip unborrowable misses, the backtest lies by reporting dollar-neutral PEAD on a net-long beat book.

## 7. Data contract

Required, point-in-time:

- Split-adjusted quarterly EPS
- Earnings **announcement timestamps** (not period-end dates)
- Split- and dividend-adjusted prices for the holding window
- ADV for liquidity filters and impact caps
- Borrow availability and fees for shorts

Not used by this spec: book value, industry map, trailing price momentum, option IV.

No restatement peeking. A revision dated after `asof` must not enter SUE. Delisted names stay until the delist date.

If you do X = use Compustat “final” EPS that overwrites the live print, the backtest lies. If you do X = treat period-end as `asof`, you trade before the number existed. If you do X = split-adjust EPS with a factor that was not known at the print, SUE is restated. If you do X = include the announcement-bar return in $R^{\mathrm{fwd}}$, you are not measuring drift.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| seasonal lag | 4 quarters | exact, not calendar-year approx |
| $\sigma$ history | 8 quarters | skip if shorter |
| decile | 10% | |
| hold | 1–6 months | drift fades after ~6m |
| rebalance | monthly or event | event = after each print |
| stale cutoff | caller-set | drop if last print too old |
| ADV cap | $1\%$ of ADV | per name |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.earnings_momentum` with:

1. `sue(eps_panel, asof) -> pd.Series` — prints after `asof` must not enter; four-quarter lag exact; refuse `sigma==0`.
2. `weights(sue, mode) -> pd.Series` — budget identities to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — never live routing.
4. `pnl(D, forward_returns, costs) -> float`.

`asof` must precede any price used for the subsequent hold. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Look-ahead on revisions.** Restated EPS after `asof` is a different number than the live print. If you do X = use the restated series, the backtest lies in the usual Compustat direction (smoother surprises).
- **Noisy $\sigma$.** Low-coverage names have unstable denominators. If you do X = keep $\sigma$ near zero instead of dropping, SUE explodes and the backtest lies about a few micro names.
- **Crowding.** The days after the print are the most crowded. If you do X = fill at mid on the print close, the backtest lies about PEAD you could not have gotten.
- **Stale SUE.** A name with no print this quarter is not a fresh surprise. If you do X = hold last quarter’s SUE forever, the backtest lies by mixing PEAD with a slow residual.

## 11. Acceptance tests

- A print dated after `asof` must not enter SUE. If bumping that print changes SUE, the implementation looks ahead and the backtest lies.
- Four-quarter lag is exact, not “last year approx”.
- Names with `sigma==0` or $<8$ quarters are dropped, not given infinite SUE.
- Weights satisfy the stated budget identities to `1e-8`.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
