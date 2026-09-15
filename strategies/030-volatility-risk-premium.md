---
rank: 30
slug: volatility-risk-premium
title: "Volatility Risk Premium"
asset_class: "volatility / indexes"
style: "short vol / index straddles"
horizon: "~1 month options, held to expiry or until a vol spike stop"
instruments: "index options, VIX futures, or variance swaps"
---

# 030. Volatility Risk Premium

| Field | Value |
|---|---|
| Popularity rank (this kit) | 30 of 101 |
| Why it sits here | Sell implied vs realized. Core hedge-fund and overlay. Sell S&P straddles when VIX exceeds trailing realized vol. |
| Aliases | short vol, VRP, sell straddles |
| Asset class | volatility / indexes |
| Style | short vol / index straddles |
| Typical horizon | ~1 month options, held to expiry or until a vol spike stop |
| Instruments | index options, VIX futures, or variance swaps |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Implied volatility on index options sits above subsequent realized volatility most of the time. That gap is the volatility risk premium. Harvest it by selling a near-ATM index straddle when a VRP proxy is positive, or by selling a variance swap struck at implied variance.

You are paid to warehouse crash and jump risk. The credit looks like income only until a gap day. Size off the left tail, not off the credit. A book that scales contracts so that this month’s premium is a round number will be too large on the next vol event.

You are not forecasting the index level. A sold ATM straddle is short absolute move. You are also not running the index-volatility-targeting overlay in file 050: that file scales long index exposure to a vol target. This file sells insurance when implied looks rich versus realized.

Typical users are overlay desks and short-vol sleeves inside multi-strategy books. The natural horizon is one listed expiry, about a month. Hold to expiry if the proxy stays positive and the stop has not fired; cover early on a pre-committed vol-spike rule. Delay-1 fills are the research default. Same-bar mids are a backtest choice, not a live book.

## 2. First principles

An ATM straddle is long absolute move and short nothing else. At expiry its payout, before premium, is the distance from strike:

$$
\lvert S_T - K \rvert = (S_T - K)_+ + (K - S_T)_+
$$

The identity is just put-call decomposition of the absolute value. Every unit the index finishes away from $K$ is paid once, whether the finish is above or below. There is no hidden delta in that expiry payoff: the two wings already span both directions. If you skip this identity and treat a short call as “the” short-vol trade, you have written a directional book.

Selling the straddle for credit $C$ therefore has terminal P&L

$$
f_T = -\lvert S_T - K \rvert + C
$$

The best case is $S_T=K$, when $f_T=C$. Break-evens sit at $K\pm C$. Outside that band the short is losing money, and there is no cap. Financing on the credit and fees shift $C$ but do not add a second kink. If you mark $C$ at mid while you would only be filled on the bid, the paper credit is fiction.

Under a diffusion, the fair $C$ is increasing in implied vol $\sigma_{\mathrm{imp}}$. Realized vol over the life is the quadratic variation of the underlying. The VRP is the gap

$$
\mathrm{VRP} = \sigma_{\mathrm{imp}} - \sigma_{\mathrm{real}}
$$

When $\mathrm{VRP}>0$ the sold straddle is rich relative to the typical path: you collected more premium than the usual realized move would have cost. It is not an arbitrage. A jump that realizes more than $\sigma_{\mathrm{imp}}$ makes $f_T$ large and negative, and a vol-of-vol spike can mark the short against you before expiry even if the index later mean-reverts. The proxy is a gate, not a lock.

A variance swap is the same bet without delta. Its payoff is linear in realized variance minus the strike (Section 4.4). Use it when listed straddles are a poor match for the variance you want to sell, or when you do not want to warehouse index delta between fills.

That is the whole strategy. Everything below is how to measure the proxy, how to size, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S_t$ | index level (SPX or the chosen underlier) |
| $K$ | straddle strike, near ATM at trade time |
| $C$ | net credit for selling the call and the put |
| $f_T$ | terminal option P&L including premium |
| $\mathrm{VIX}_{t_0}$ | VIX (or the matching implied-vol index) at decision time, in vol points |
| $\sigma^{\mathrm{realized}}$ | realized vol of the index, same units as VIX |
| $N$ | variance notional if the swap implementation is used |
| $v(T)$ | realized variance over the contract |
| $K_{\mathrm{var}}$ | variance-swap strike |
| $I$ | gross premium or variance notional budget |
| $L_{\max}$ | designed max loss used for sizing |

## 4. Mathematics

### 4.1 VRP proxy

Take a lookback that **ends before** the fill. Compare implied vol at the start of the window to realized vol over the window, in the same units (percent, annualized):

$$
\mathrm{VRP}_t = \mathrm{VIX}_{t_0} - \sigma^{\mathrm{realized}}_{\mathrm{SPX}}(t_0,t)
$$

Default: $t_0$ is the start of the current month, $t$ is today, realized vol uses log returns and $F=252$. Both legs of the difference must share units: mixing VIX points with decimal realized vol scales the gate by 100 and will keep you short forever or never. The window must not include the fill-bar return; that return is the first piece of the holding-period path, not of the decision. Sign rule:

- $\mathrm{VRP}_t > 0$ — implied rich vs realized → **sell** the ATM straddle (or sell variance)
- $\mathrm{VRP}_t \le 0$ — no short-vol entry; stay in cash or cover if already short

The gate is conservative on purpose. A small positive VRP after costs is not an invitation to lever. If the proxy is non-positive, a flat blotter is a valid output; inventing a “light short” because last month was profitable is a different spec.

### 4.2 Short ATM straddle

Call and put with the same $K$ and expiry $T$. Terminal P&L including credit is

$$
f_T = -(S_T-K)_+ - (K-S_T)_+ + C
$$

This is the same identity as Section 2, written with the two intrinsic pieces visible so a unit test can check each wing. Maximum credit is $C$ (if $S_T=K$). Loss is unbounded as $\lvert S_T-K\rvert$ grows. Break-evens are $K\pm C$, ignoring financing. Early assignment on American options, or an index halt that prevents a cover, can move you off this European-style path; log that as an event, do not interpolate a fake $S_T$.

### 4.3 Optional gamma hedge

A delta-hedged short straddle converts the bet into theta versus realized variance. After each move in $S$, trade the index so net delta stays near 0. Hedge P&L plus theta equals (up to discrete-hedge error) a short realized-variance stream. In a trend the hedge buys high and sells low; that cost can exceed $C$. Treat the hedge as optional, not as insurance against a jump. A gap through the strike is not hedgeable with a lag-1 delta, which is why $L_{\max}$ still has to assume an unhedged jump.

### 4.4 Variance-swap implementation

If listed straddles are a poor match, sell a variance swap with notional $N$ and strike $K_{\mathrm{var}}$. Payoff at $T$ is

$$
P(T) = N\bigl(v(T)-K_{\mathrm{var}}\bigr)
$$

Positive $N$ is long variance. This file’s harvest is the short, so the held notional is $-N$ in that identity when the gate says sell. The strike $K_{\mathrm{var}}$ is implied variance, not implied vol; converting a 20 vol-point VIX into $0.20$ and then forgetting to square it is a units bug. Costs and a variance cap, if the contract has one, sit outside this display line and must still enter P&L.

with realized variance (mean of $R$ **not** subtracted)

$$
v(T) = \frac{F}{T}\sum_{t=1}^{T} R(t)^2, \qquad R(t)=\ln\frac{S(t)}{S(t-1)}
$$

This is quadratic variation, not a sample variance. Subtracting $\bar R$ or using $T-1$ in the denominator will pass a naive vol test and fail every swap confirmation. Short variance means holding $-N$ in that identity. Use $F=252$ on trading-day bars. Jump days stay in the sum; censoring the largest $R(t)^2$ is a different contract.

### 4.5 Holding-period P&L

For options, mark to mid (or to the side you would trade) from fill to next decision, plus financing on the credit, minus costs. Report:

- net P&L over $L_{\max}$ or over $I$
- annualized Sharpe on **non-overlapping** holding-period returns
- one-way turnover of the option book

$$
\mathrm{turnover}_t = \frac{1}{2}\sum_j \lvert w_{j,t} - w_{j,t-1}\rvert
$$

Turnover here is on option-line weights, not on the index. Rolling every week because the ATM strike moved one tick will look like a high Sharpe on a mid-to-mid backtest and a cost sink on bid/ask. If you report Sharpe, use non-overlapping holds so a one-month option is not counted twelve times a year as if it were independent.

## 5. Step-by-step algorithm

1. **Universe.** One liquid index (default SPX listed options). Alternative: VIX futures or OTC/listed variance. Skip single-name straddles unless a separate spec calls for them; index VRP is typically larger, and a single-name short mixes idiosyncratic jump risk into a premium you measured on the index. This step exists so the agent does not silently swap in AAPL options because the chain is easier to download.
2. **Proxy.** Compute $\mathrm{VRP}_t$ from VIX (or the option-implied ATM vol) and realized vol on a window ending strictly before $t_{\mathrm{fill}}$. The proxy is the only entry signal. Building it with a window that includes today is look-ahead: today’s return is part of what the short will pay.
3. **Gate.** If $\mathrm{VRP}_t \le 0$, emit a flat blotter (or a cover of any open short). If $\mathrm{VRP}_t > 0$, continue. The gate exists so a rich-implied story does not keep you short after realized has already caught up. Covering when the proxy dies is part of the spec, not an optional overlay.
4. **Instrument.** Pick the nearest listed expiry with tenor about 1 month. Strike $K$ is the listed strike nearest to $S$ (or the VIX-implied forward). Matching tenor to the VIX window keeps the proxy and the option on the same horizon. A weekly expiry against a month-to-date VIX is a mixed object.
5. **Size.** Set contracts so that a designed $L_{\max}$ path (default: a 2008-like vol event, or a $4\sigma$ index move) does not exceed the loss budget. Do **not** size off $C$. This step exists because the premium is small relative to the tail; sizing off credit is how short-vol books blow up.
6. **Blotter.** Sell the call and the put (or sell variance). Convert to contracts, round to lot size, emit intents. Do not route live orders. Both wings must be present; a one-legged fill is a directional book.
7. **Stops.** Cover on a vol-spike rule (e.g. VIX above a trailing quantile) or a delta/gamma breach. Optional: gamma-hedge until the stop. The stop is pre-committed so a drawdown does not become an unstated “hold to expiry” rewrite of $L_{\max}$.
8. **Rebalance.** Hold to expiry, or roll at a fixed tenor. Decision data at $t$ uses only information with timestamp $< t_{\mathrm{fill}}$. Rolling without a new proxy is carrying last month’s gate into a new contract.

## 6. Execution protocol

- Default fill: next close after the proxy is known. Delay-0 same-bar fills are research-only. If you fill on the same print that just spiked VIX, the proxy and the credit are not contemporaneous in the way the identity assumes.
- Prefer selling on the bid. Do not size through listed open interest. A backtest that sells a thousand lots through 50 lots of open interest is not this spec.
- If the short cannot be held (assignment, halt, missing chain), flatten both legs. Do not leave a naked call or a naked put. A one-wing residual is a directional crash bet you did not size.
- Mandatory crash playbook: pre-commit $L_{\max}$ and the vol-spike cover rule before the first fill. Changing the stop after a loss is a different strategy.

## 7. Data contract

Required, point-in-time:

- Index level and listed option chain (bid/ask, strike, expiry, open interest)
- VIX or a matching implied-vol index, timestamped before the fill
- Realized-vol inputs: split-adjusted index returns on the proxy window
- Contract multipliers and exchange calendars

Optional: VIX futures, variance-swap strikes, borrow if a short-vol ETN overlay is used.

Not used by this spec: book value, earnings, SUE, industry maps, single-name residuals.

No restatement peeking. Use only quotes that existed before $t_{\mathrm{fill}}$. A revised VIX print published after the close does not change the $t$ decision. If the chain is missing at $t$, the blotter is flat; do not borrow tomorrow’s expiry.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor | ~1 month | listed expiry nearest 20–30 trading days |
| strike | ATM | nearest listed $K$ to $S$ |
| proxy lookback | month-to-date | VIX at $t_0$ minus realized to $t$ |
| $\sigma^\ast$ target | unused | this file is a VRP harvest, not vol targeting |
| $L_{\max}$ path | caller-set | size off this, not off $C$ |
| gamma hedge | off | on → delta-hedge the short straddle |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.volatility_risk_premium` with:

1. `vrp_proxy(vix, realized_vol, t0, t) -> float` — $\mathrm{VRP}_t$, no look-ahead.
2. `straddle_pnl(S_T, K, C) -> float` — matches $-(S_T-K)_+-(K-S_T)_++C$ to `1e-8`.
3. `size(L_max, chain, I) -> dict` — contract counts with designed $L_{\max}$ respected.
4. `blotter(signal, chain, size, lot) -> list[OrderIntent]` — sell call and put (or sell variance), never live routing.
5. `pnl(positions, marks, costs) -> float` — option or variance-swap identity minus costs.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Vol spike.** A selloff reprices implied vol and the short straddle loses on both gamma and vega. The cover rule can still fill at a worse credit than the paper stop assumed if you delay-1 through the event.
- **Left tail.** Loss is unbounded in $S$; a gap through the break-even is not hedgeable with a lag-1 delta. Overnight index futures gaps are the usual path.
- **Gamma-hedge bleed.** In a one-way trend the hedge pays more than $C$. Turning the hedge on after the trend has started is hindsight, not insurance.
- **Sizing off credit.** Small $C$ with huge $L_{\max}$ is how short-vol books blow up. If $C$ halves, contracts must not double unless $L_{\max}$ still fits.
- **Proxy units.** Mixing VIX points with decimal realized vol, or using a window that includes the fill bar, produces a gate that is not this spec.
- **Missing wing.** Assignment or a halt that leaves only the call or only the put turns the book into a directional short.

## 11. Acceptance tests

- $\mathrm{VRP}_t$ computed at $t$ is invariant to permuting VIX and returns after $t$. If shuffling tomorrow’s VIX changes today’s gate, the window leaked.
- Toy path $S_T=K$ → $f_T=C$. Toy path $S_T=K+x$ → $f_T=C-\lvert x\rvert$.
- Variance-swap identity: $v(T)$ uses $\sum R(t)^2$ with denominator $T$, not $T-1$, and does not subtract $\bar R$.
- If $\mathrm{VRP}_t\le 0$, the blotter is flat (or a cover), never a new short.
- Adding linear costs $\tau$ weakly decreases P&L. A test that “absorbs” costs into a higher $C$ is not this spec.
- Size under a stated $L_{\max}$ path stays inside that loss; increasing $C$ must not increase contracts.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
