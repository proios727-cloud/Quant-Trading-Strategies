---
rank: 64
slug: implied-volatility-equities
title: "Implied Volatility (Equities)"
asset_class: "equities"
style: "option-implied cross-section"
horizon: "Monthly change in IV; hold the subsequent month."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 064. Implied Volatility (Equities)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 64 of 101 |
| Why it sits here | Stocks whose call IV rose outperform; stocks whose put IV rose underperform. Listed-option overlay on the equity book. |
| Aliases | call/put IV change sort, option-implied equity cross-section |
| Asset class | equities |
| Style | option-implied cross-section |
| Typical horizon | Monthly change in IV; hold the subsequent month. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Long the top decile of **call-IV increase**, short the top decile of **put-IV increase**. Variant: sort on $\Delta\mathrm{IV}_{\mathrm{call}}-\Delta\mathrm{IV}_{\mathrm{put}}$. This is **not** a single-name vol sale. It is an equity cross-section that uses IV **changes** as the signal. Rebalance monthly on the equity, not on the options.

You are betting that a bullish tilt in the call surface (call IV up) continues into next month’s *stock* return, and that a bearish tilt in the put surface (put IV up) continues as underperformance. You are not selling calls or puts, not sorting on IV *level* (that is a vol-sale-adjacent book), and not claiming the optionable universe is the equity universe.

Typical user: a quant equity sleeve with a listed-option IV history that wants an overlay next to price momentum. Horizon intuition: measure one-month IV changes at month-end, hold the stock the subsequent month, delay-1 fill. The days after a vol spike are not this spec unless you change the horizon.

If you mix raw IV level with IV change, emit option orders, or let a name that was not optionable at $t$ enter the $t$ sort, the backtest is a different (often better-looking) object.

## 2. First principles

Let $\mathrm{IV}^{c}_i$ be a matched-tenor, matched-moneyness call implied vol (default: ATM 30-day) and $\mathrm{IV}^{p}_i$ the corresponding put implied vol. The one-month changes are

$$
\Delta\mathrm{IV}^{c}_i = \mathrm{IV}^{c}_i(t) - \mathrm{IV}^{c}_i(t-1\mathrm{m})
$$

Call IV now minus call IV one month ago, same tenor/moneyness. Only IV dated $\le$ the sort. A later surface print cannot rewrite $\Delta\mathrm{IV}^{c}$. Corporate actions: compare surfaces that correspond to the adjusted equity, or a split looks like an IV jump. Missing call IV → drop unless a documented one-sided sort.

$$
\Delta\mathrm{IV}^{p}_i = \mathrm{IV}^{p}_i(t) - \mathrm{IV}^{p}_i(t-1\mathrm{m})
$$

Same for puts. Matched tenor and moneyness with the call leg; mixing 30d ATM calls with 60d OTM puts is a different signal. Illiquid names have jumpy IV — the change can be measurement error. Quality flags (nonzero option volume) exist so you do not sort on a model mark.

A rise in call IV, holding put IV fixed, is a bullish tilt in the option surface: call demand (or bullish tail pricing) increased. A rise in put IV is a bearish tilt. The equity-book hypothesis is that those tilts continue into the next month’s stock return:

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} \bigm| \Delta\mathrm{IV}^{c}_i\bigr] \ \text{increasing in }\Delta\mathrm{IV}^{c}_i
$$

Empirical claim: larger call-IV *increase*, higher next-month expected *equity* return. Not a statement about selling the call. Conditioning is on $\Delta\mathrm{IV}^{c}$ known at the sort, not on next month’s IV. If $\lambda$ is fit on $R^{\mathrm{fwd}}$, you fitted the test.

$$
\mathbb{E}\bigl[R_i^{\mathrm{fwd}} \bigm| \Delta\mathrm{IV}^{p}_i\bigr] \ \text{decreasing in }\Delta\mathrm{IV}^{p}_i
$$

Larger put-IV increase, lower expected equity return — hence short the top decile of $\Delta\mathrm{IV}^{p}$. Opposite slope from the call side. That is why the two-decile construction uses two *separate* rankings, not one ranking on average IV.

So you long names with the largest call-IV increase and short names with the largest put-IV increase. The difference score

$$
x_i = \Delta\mathrm{IV}^{c}_i - \Delta\mathrm{IV}^{p}_i
$$

is the one-sort variant of the same identity. Rising call IV and falling put IV is the long extreme of $x_i$. This variant forces a single ranking; the two-decile construction can long a name that is not in the put-IV short set (and vice versa), then net overlaps.

You do not sell the calls or the puts. The holdings are cash equities (long/short the stocks). Raw IV **level** is a different signal; do not mix it with IV **change**.

That is the whole strategy. Everything below is the two rankings, the difference variant, and the optionable-universe data contract.

### Worked intuition

Two names, ATM 30-day IV, already matched. CallUp: call IV went $25\%\to 30\%$ ($\Delta\mathrm{IV}^{c}=+5$ pts), put IV $25\%\to 24\%$ ($\Delta\mathrm{IV}^{p}=-1$). PutUp: call IV $20\%\to 19\%$, put IV $20\%\to 28\%$. Two-decile toy: long CallUp (top call-IV increase), short PutUp (top put-IV increase). Difference $x$: CallUp has $x=+6$, PutUp has $x=-9$ — same long/short. The blotter is stock shares, not option contracts. If CallUp was not optionable last month, it cannot enter this month’s sort even if it has a surface today. If you sorted on IV *level* 30% versus 19%, you would be in a different, vol-sale-adjacent book.

## 3. Notation

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | optionable names after liquidity filters |
| $\mathrm{IV}^{c}_i$ | call implied vol, matched tenor/moneyness |
| $\mathrm{IV}^{p}_i$ | put implied vol, same match |
| $\Delta\mathrm{IV}^{c}_i,\,\Delta\mathrm{IV}^{p}_i$ | one-month changes |
| $x_i$ | $\Delta\mathrm{IV}^{c}_i-\Delta\mathrm{IV}^{p}_i$ |
| $w_i$ | equity portfolio weight (positive = long) |
| $I$ | gross dollars |
| $D_i = I w_i$ | signed dollar holdings in the **stock** |
| $Q_i$ | signed stock shares |

Dollar-neutral means $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$.

## 4. Mathematics

### 4.1 Two-decile construction

Dollar-neutral book:

- Long: top decile of $\Delta\mathrm{IV}^{c}$
- Short: top decile of $\Delta\mathrm{IV}^{p}$

The long and short universes can overlap (a name can have both call IV and put IV up). If a name is in both tops, it is netted in $w_i$, not held long and short.

Separate rankings on purpose. A name with both surfaces up can appear in both deciles; netting exists so you do not emit a long and a short in the same stock. If you instead short the *bottom* of $\Delta\mathrm{IV}^{c}$, you have a call-IV high-minus-low, which is not this construction.

Modulus-uniform on the two legs after netting, or equal-weight inside each decile then net. Document the choice. Default: equal-weight each decile, then $w \leftarrow w / \sum\lvert w\rvert$ with $\sum w$ repaired to 0.

### 4.2 Difference variant

Sort on

$$
x_i = \Delta\mathrm{IV}^{c}_i - \Delta\mathrm{IV}^{p}_i
$$

One number per name: call-IV change minus put-IV change. Long top decile of $x_i$, short the bottom. A name with rising call IV and falling put IV is long in this variant. This is not the same book as §4.1: overlaps are handled by the algebra of $x$ instead of by netting two deciles. Document `variant`.

Long the top decile of $x_i$, short the bottom. A name with rising call IV and falling put IV is long in this variant.

### 4.3 Weights and P&L

Shares, ignoring lot-size until the blotter:

$$
Q_i = \frac{I w_i}{P_i(t_{\mathrm{fill}})}
$$

**Stock** shares at the equity fill price. Not option contracts, not delta-shares of a listed call. Using option mid in the denominator would size a different instrument. Lot rounding uses a cash bucket.

Let $R_i^{\mathrm{fwd}}$ be the simple **equity** return from fill to next rebalance, including dividends. Then

$$
\mathrm{P\&L} = \sum_i D_i R_i^{\mathrm{fwd}} - \mathrm{costs}
$$

Equity P&L. Option P&L does not belong here. Borrow costs on the put-IV short leg do. If you do X = mark with option-implied moves instead of stock returns, you are not testing this spec. Delay-1: IV dated $\le$ sort, fill after.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** holding-period returns, and one-way turnover

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_i \lvert w_{i,t} - w_{i,t-1}\rvert
$$

Monthly equity turnover of the IV-change sort. If you do X = trade the option to “implement the signal,” turnover and costs are a different business. Overlapping holds inflate Sharpe if treated as independent.

## 5. Step-by-step algorithm

1. **Universe.** Names with listed options that actually trade. Liquidity filters on the stock (price, ADV) and on the option (nonzero volume or a documented IV quality flag). Keep delisted names until the delist date. Survivorship in the **optionable** universe: a name that was not optionable at $t$ cannot enter the $t$ sort. This step exists so you do not sort on a surface that a live book could not have seen.
2. **IV surface.** Take ATM 30-day call and put IV, or a documented matched tenor/moneyness. Corporate actions: use the surface that corresponds to the adjusted equity. Mismatched tenor is a different signal; this step exists to freeze the match.
3. **Changes.** $\Delta\mathrm{IV}^{c}$ and $\Delta\mathrm{IV}^{p}$ over the previous month, using only IV dated $\le$ the sort. Drop missing either side unless the caller is running a one-sided sort (document that). Look-ahead IV is the usual vendor sin.
4. **Rank.** Default: long top decile of $\Delta\mathrm{IV}^{c}$, short top decile of $\Delta\mathrm{IV}^{p}$. Variant: sort $x_i$. Separate rankings are the product; mixing with IV level is a bug.
5. **Size.** Equal-weight legs, net overlaps, enforce dollar-neutrality. Netting exists so dual-top names are not double-counted as long and short.
6. **Caps.** Clip $\lvert D_i\rvert$ at a fraction of **stock** ADV. Repair the budget; do not silently drop the short leg. Option ADV is not the cap; you trade stock.
7. **Blotter.** Equity shares only. Round to lot size, emit intents. Do not route live orders. Do not emit option orders. Option orders would make this a vol book.
8. **Rebalance.** Monthly on the equity. Hold the subsequent month. Delay-1 fill. Filling on the last IV print’s close without delay captures a stock move that may have caused the IV change.

## 6. Execution protocol

- Monthly rebalance on the equity, not the options. If you do X = roll listed options to “hold the signal,” costs and greeks are a different spec and the backtest lies about this file.
- Separate rankings for call vs put changes. Do not mix raw IV level with IV change. If you do X = sort on IV level and label it $\Delta\mathrm{IV}$, the backtest lies about change-vs-level.
- Borrow required for shorts. If a name cannot be shorted, drop it and rebuild the put-IV (or low-$x$) leg. If you do X = skip unborrowable put-IV names, the backtest lies by reporting dollar-neutral IV-change on a net-long call-IV book.

## 7. Data contract

Required, point-in-time:

- Call and put implied vol history at the documented tenor/moneyness (default ATM 30d)
- Option volume or a quality flag (IV on a non-traded option is not a signal)
- Split- and dividend-adjusted equity prices for fills and P&L
- Corporate-action timestamps (so IV is not compared across an unadjusted split)
- ADV on the stock for liquidity filters and impact caps
- Borrow availability and fees for shorts
- Optionable-universe membership dated $\le$ the sort (survivorship)

Not used by this spec: book value, SUE, earnings timestamps, industry map, trailing equity momentum — unless you are mixing this sleeve in [`047-multifactor-portfolio.md`](047-multifactor-portfolio.md).

No restatement peeking. Delisted names stay until the delist date.

If you do X = use a vendor IV that overwrites last month’s surface, $\Delta\mathrm{IV}$ is restated. If you do X = include names that listed options only after $t$, optionable survivorship inflates the sort. If you do X = compare IV across an unadjusted split, $\Delta\mathrm{IV}$ is a corporate action. If you do X = fill ADV from option volume, you capped the wrong market.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| IV tenor | 30d | matched |
| moneyness | ATM | matched call/put |
| construction | two-decile | variant: sort $x_i$ |
| decile | 10% | |
| hold | 1 month | subsequent month |
| ADV cap | $1\%$ of stock ADV | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.implied_volatility_equities` with:

1. `iv_changes(iv_call, iv_put, asof, tenor, moneyness) -> (d_call, d_put)` — no look-ahead; refuse raw IV **level** as a substitute.
2. `weights(d_call, d_put, variant) -> pd.Series` — separate rankings for call vs put, or $x_i$; budget identities to `1e-8`.
3. `blotter(weights, prices, I, lot) -> list[OrderIntent]` — **equity** intents only; never live routing.
4. `pnl(D, forward_equity_returns, costs) -> float`.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **IV noise.** Illiquid names have jumpy IV; the change is measurement error. If you do X = skip the volume quality flag, the backtest lies about a signal that was a model mark.
- **Overlap with momentum.** Rising call IV often sits on names that already ran. If you do X = residualize against 12-1 without saying so, you have a different sleeve.
- **Listing bias.** The optionable universe is not the equity universe. If you do X = apply these ranks to names that were not optionable at $t$, the backtest lies through listing survivorship.
- **Level vs change.** Sorting on IV level is a different (vol-sale-adjacent) book. If you do X = substitute level for $\Delta\mathrm{IV}$, the backtest lies about this spec.

## 11. Acceptance tests

- A name with rising call IV and falling put IV is long in the difference variant.
- Separate rankings: top $\Delta\mathrm{IV}^{c}$ is long, top $\Delta\mathrm{IV}^{p}$ is short, even if those sets differ.
- IV dated after `asof` must not enter $\Delta\mathrm{IV}$. If a later surface changes $\Delta\mathrm{IV}$, the implementation looks ahead and the backtest lies.
- Blotter contains equity intents only (no option contracts). If an option order appears, the test must fail.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
