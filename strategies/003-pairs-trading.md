---
rank: 3
slug: pairs-trading
title: "Pairs Trading"
asset_class: "equities"
style: "mean-reversion / relative value"
horizon: "Formation on a long correlation window (months to a year). Holding days to weeks until spread mean-reverts or a stop hits."
instruments: "listed equities (liquid names; typically a few hundred to a few thousand)"
---

# 003. Pairs Trading

| Field | Value |
|---|---|
| Popularity rank (this kit) | 3 of 101 |
| Why it sits here | The textbook statistical-arbitrage trade. Default interview question and the seed of every cluster mean-reversion book. |
| Aliases | relative-value pair, two-leg residual fade |
| Asset class | equities |
| Style | mean-reversion / relative value |
| Typical horizon | Formation on a long correlation window (months to a year). Holding days to weeks until spread mean-reverts or a stop hits. |
| Instruments | listed equities (liquid names; typically a few hundred to a few thousand) |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Find two historically highly correlated stocks. When they dislocate, short the rich one, buy the cheap one, dollar-neutral. This is single-cluster mean-reversion with $N=2$ legs.

You are betting that a recent *relative* gap between two names that usually move together will fade, not that either name is cheap versus the market. The common move — sector tape, factor flow, a rate shock — is subtracted by construction. What remains is a two-name residual. Fade that residual with equal dollars, opposite signs.

You are not betting on the sector, not running a one-legged directional book, and not claiming cointegration is an identity. Correlation on a formation screen is a filter, not a promise that the next dislocation reverts. News, mergers, and fraud can make the residual a new mean.

Typical user: a stat-arb desk or an interview-level prototype of the $N$-name industry fade in [`014-mean-reversion-single-cluster.md`](014-mean-reversion-single-cluster.md). Horizon intuition: screen on months to a year of co-movement, measure the dislocation on a shorter window that ends before the fill, hold days to weeks until the residual comes back or a stop kills the trade. If you fit the pair on the same window you trade, or open only the cheap leg, the backtest is not pairs trading.

## 2. First principles

Write each leg’s formation return as a common factor plus an idiosyncratic shock:

$$
R_A = F + \varepsilon_A, \qquad R_B = F + \varepsilon_B
$$

Both names share $F$ (the pair’s co-move). Anything that hits both — a sector ETF flow, a rate day — sits in $F$ and will be removed when you demean. The trade lives entirely in $\varepsilon_A$ and $\varepsilon_B$. If the two names do not actually share a factor, demeaning still produces opposite residuals, but they are not “idiosyncratic versus a real common move”; they are just plus and minus half the spread of two unrelated returns. That is why the correlation screen exists *before* this identity.

$F$ is the shared move (sector, style, or the pair’s own co-move). The equal-weight pair mean is the sample estimate of $F$:

$$
\bar R = \tfrac12(R_A + R_B) = F + \tfrac12(\varepsilon_A + \varepsilon_B)
$$

With two names, the pair mean is the midpoint of the two returns. It estimates $F$ plus the average of the two shocks. You cannot recover $F$ exactly from two observations; you can only subtract the midpoint. That is enough to make the residuals opposites. If you used a third name’s return as $F$, you would be running a different (triplet) book.

The residuals are then

$$
\tilde R_A = R_A - \bar R, \qquad \tilde R_B = R_B - \bar R
$$

Each residual is the name versus the pair midpoint. A positive $\tilde R_A$ means A beat the pair over the formation window: rich. A negative residual means lagged: cheap. This step is arithmetic, not a forecast. Skip it and you are trading two raw returns, i.e. a directional two-name book.

By construction they sum to zero and are opposites:

$$
\tilde R_A + \tilde R_B = 0 \quad\Rightarrow\quad \tilde R_B = -\tilde R_A
$$

With $N=2$, dollar-neutrality of a fade $D \propto -\tilde R$ is automatic if you put equal dollars on both legs. There is no third residual to absorb. If your code produces two residuals that do not sum to zero, the demean is wrong. This identity is why opening one leg alone is not a pair: the other residual is not optional.

Mean-reversion says a large idiosyncratic dislocation tends to fade:

$$
\mathbb{E}[\varepsilon_{A,t+1} \mid \varepsilon_{A,t}] \approx -\lambda\,\varepsilon_{A,t}, \qquad \lambda \in (0,1)
$$

This is the bet, not the identity. $\lambda\in(0,1)$ says the shock shrinks; it does not say it hits zero tomorrow. If $\lambda\le 0$, the pair is trending apart and the fade loses. Conditioning is on the *past* residual; using the holding-period residual on the right-hand side would be look-ahead.

So the next-period expected residual has the **opposite sign** of $\tilde R$. Short the rich name ($\tilde R > 0$), buy the cheap name ($\tilde R < 0$), equal dollars. You are not betting on the sector. You are betting that the pair-relative surprise dies out.

That is the whole strategy. Everything below is how to measure the two returns, how to size the two legs, and how not to open one leg alone.

### Worked intuition

Call the names A and B. Over a formation window that already ended, A returned $+6\%$ and B returned $+2\%$. Pair mean is $+4\%$. Residuals: A is $+2\%$ (rich → short), B is $-2\%$ (cheap → long). At fill prices $P_A=50$ and $P_B=25$, a $\$100$ gross book puts $\$50$ short A (1 share) and $\$50$ long B (2 shares). Dollar neutrality: $-50+50=0$. If both names then rally $3\%$ with the sector, the pair P&L is about zero before costs; you needed B to *outperform* A from here, not for the sector to rise. If A gaps $+20\%$ on a takeover print, the residual is a new mean — flatten both legs, do not “wait for the spread.”

## 3. Notation

| Symbol | Definition |
|---|---|
| $(A,B)$ | the two names in the pair |
| $P_A(t),\,P_B(t)$ | split- and dividend-adjusted prices |
| $t_1 < t_2 \le t_\ast$ | formation window ends at $t_2$; fill at $t_\ast$ |
| $R_A,\,R_B$ | formation returns (simple or log) |
| $\bar R$ | pair mean $\tfrac12(R_A+R_B)$ |
| $\tilde R_A,\,\tilde R_B$ | residuals $R - \bar R$ |
| $Q_A,\,Q_B$ | signed share holdings (positive = long) |
| $I$ | gross dollars on the pair |
| $D_i = P_i Q_i$ | signed dollar holdings |

Dollar-neutral means $P_A Q_A + P_B Q_B = 0$. Combined with the gross budget this is $P_A\lvert Q_A\rvert + P_B\lvert Q_B\rvert = I$.

## 4. Mathematics

### 4.1 Formation returns

Take a lookback window $[t_1, t_2]$ that **ends before** the fill. Simple returns:

$$
R_A = \frac{P_A(t_2)}{P_A(t_1)} - 1
$$

This is A’s simple return over the dislocation window, not the long correlation screen. $t_2$ must be strictly before the fill so the residual is known before you trade. If $t_2$ is the fill bar, you are using the same print in the signal and the entry. Missing $P_A(t_1)$ or $P_A(t_2)$ means refuse the pair, not stitch a stale quote.

$$
R_B = \frac{P_B(t_2)}{P_B(t_1)} - 1
$$

Same definition on the other leg, same window. Mixing a 5-day return on A with a 20-day return on B manufactures a residual that is not a pair dislocation. Both prices must be split-adjusted; a split on B only would look like a huge cheap residual.

Log returns (interchangeable with simple returns when returns are small):

$$
R_A = \ln\frac{P_A(t_2)}{P_A(t_1)}
$$

Logs make a round-trip of $+x$ then $-x$ net to zero, which matches the fade story slightly better on large moves. This is still A only; you have not demeaned yet. Pick logs or simple *before* ranking, not after seeing which residual looks better.

$$
R_B = \ln\frac{P_B(t_2)}{P_B(t_1)}
$$

Same log definition on B. If you log A and simple-return B, $\bar R$ is meaningless and the residuals are not opposites in any clean sense. Pick one definition and use it on both legs. Do not mix.

### 4.2 Pair residual

Demean inside the pair:

$$
\bar R = \tfrac12(R_A + R_B)
$$

Midpoint of the two formation returns. This is the estimated common move. Using a volume-weighted or beta-weighted mean is a different spec (closer to the weighted-regression file). Here both names get equal voice in $F$.

$$
\tilde R_A = R_A - \bar R
$$

A versus the midpoint. Sign of this residual is the whole signal for A. If you skip demeaning and short the name with the higher raw return versus zero, you are shorting the stronger absolute tape, which may be the sector.

$$
\tilde R_B = R_B - \bar R
$$

B versus the same midpoint. Must equal $-\tilde R_A$. If it does not, stop: the demean is wrong.

Sign rule:

- $\tilde R > 0$ — name beat the pair → **rich → short**
- $\tilde R < 0$ — name lagged the pair → **cheap → long**
- $\tilde R = 0$ — no dislocation, stay flat

### 4.3 Dollar-neutral share counts

At fill prices $P_A, P_B$ (time $t_\ast$), gross $I$, dollar-neutral:

$$
P_A\lvert Q_A\rvert + P_B\lvert Q_B\rvert = I
$$

Gross dollars on the two legs sum to $I$. This is the budget. If you size shares first and check dollars later, lot rounding can break both this and neutrality. Enforce this identity *before* rounding.

$$
P_A Q_A + P_B Q_B = 0
$$

Signed dollars sum to zero: one long, one short, equal dollars. Together with the gross identity, each leg is $I/2$ in absolute dollars. If this fails, you have a net directional pair.

Signs: $Q<0$ on the rich name, $Q>0$ on the cheap name. The equal-dollar solution is

$$
Q_{\mathrm{rich}} = -\frac{I}{2 P_{\mathrm{rich}}}
$$

Short enough shares of the rich name that the dollar short is half the gross. The minus sign is the fade: rich gets shorted. Using $P_{\mathrm{cheap}}$ in this denominator would size the wrong leg. If $P_{\mathrm{rich}}$ is a later print than $t_\ast$, you resized on look-ahead.

$$
Q_{\mathrm{cheap}} = +\frac{I}{2 P_{\mathrm{cheap}}}
$$

Long half the gross in the cheap name. Proof of neutrality: $P_{\mathrm{rich}} Q_{\mathrm{rich}} + P_{\mathrm{cheap}} Q_{\mathrm{cheap}} = -I/2 + I/2 = 0$. Proof of gross: $I/2 + I/2 = I$. If one leg then clips on ADV, you must shrink the other; keeping the cheap long at $I/2$ while clipping the short is a one-legged book.

Proof of neutrality: $P_{\mathrm{rich}} Q_{\mathrm{rich}} + P_{\mathrm{cheap}} Q_{\mathrm{cheap}} = -I/2 + I/2 = 0$. Proof of gross: $I/2 + I/2 = I$.

### 4.4 Holding-period P&L

Let $R_i^{\mathrm{fwd}}$ be the simple return from fill to exit, including dividends. Then

$$
\mathrm{P\&L} = D_A R_A^{\mathrm{fwd}} + D_B R_B^{\mathrm{fwd}} - \mathrm{costs}
$$

Two-leg mark-to-market minus two-leg costs. Dividends on the cheap long are income; borrow and dividends on the rich short are costs. If you do X = mark only the long leg “until the short fills,” the backtest lies by warehousing overnight directional risk that the spec forbids.

Report net return on gross $I$, annualized Sharpe on **non-overlapping** round-trips, and one-way turnover on the pair book.

## 5. Step-by-step algorithm

1. **Universe.** Liquid names; same sector preferred, not required. Borrow available on any name that can be the rich (short) leg. Keep delisted names until the delist date. This step exists so the pair is tradable on both legs. A delist during formation is a real outcome, not a reason to drop the pair from history.
2. **Formation screen.** On a rolling window of months to a year that **ends at or before** $t_1$, keep pairs whose correlation (or cointegration) exceeds a threshold. Do not fit the screen on the residual window you trade. This step exists to pick names that actually share $F$. If you do X = screen on $[t_1,t_2]$, the backtest lies by selecting pairs *because* they just dislocated.
3. **Signal.** Compute $R_A, R_B$ on $[t_1, t_2]$ with $t_2 < t_\ast$. Demean. Open when $\lvert\tilde R\rvert$ exceeds a threshold, or when a residual z-score exceeds $c$. The threshold exists so tiny midpoint noise does not flip the book every day. The window end before fill exists so the residual is knowable.
4. **Size.** Set $Q_{\mathrm{rich}}$ and $Q_{\mathrm{cheap}}$ from the equal-dollar identities. Enforce both dollar identities **before** rounding. Rounding first, then checking neutrality, is how one-share residuals become accidental market bets.
5. **Caps.** Clip each leg at a fraction of ADV (default $1\%$). If one leg clips, shrink the other so neutrality still holds; never open one leg. This step exists because the cheap name is often the less liquid one. A one-legged open is a directional trade.
6. **Blotter.** Round to lot size, park the residual in a cash bucket, emit intents for **both** legs together. Do not route live orders. “Together” is the product: two intents or none.
7. **Exit.** Residual back inside a band, time stop, or hard loss stop. Corporate actions: adjust for splits the same day. If one name gaps on news, flatten both legs. The stop exists because fade is a bet, not an identity; the flatten-on-news rule exists because $\varepsilon$ can jump to a new mean.

## 6. Execution protocol

- Trade both legs simultaneously. Never open one leg. A futures hedge of residual overnight is allowed; a one-legged cash book is not. If you do X = fill the cheap long at the close and the rich short next morning, the backtest lies by hiding overnight beta.
- Default fill: next close after the residual is known. Delay-0 close-to-close is research-only. If you do X = use the $t_2$ close as both residual and fill, the backtest lies by trading the print that created $\tilde R$.
- If the rich name cannot be shorted, refuse the pair. Do not keep the cheap long and skip the short. If you do X = skip unborrowable rich names, the backtest lies by turning pairs into a long-only “cheap versus midpoint” sleeve.
- Gap-on-news: the mean-reversion thesis may be dead. Flatten.

## 7. Data contract

Required, point-in-time:

- Split- and dividend-adjusted prices on the correlation window, the residual window, and the holding window
- ADV for liquidity filters and impact caps
- Borrow availability and fees on the rich leg
- Optional: point-in-time industry map if the pair screen is restricted to the same sector

Not used by this spec: book value, earnings, SUE.

No restatement peeking. Delisted names stay in the formation sample until the delist date.

If you do X = compute correlation on a sample that includes the hold, the screen looks ahead. If you do X = use unadjusted prices, a split looks like a dislocation. If you do X = take borrow as of today for a 2010 pair, the backtest lies about whether the rich leg was shortable.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| return type | log | simple returns allowed if $\lvert R\rvert$ is small |
| correlation window | 12 months | ends at or before $t_1$ |
| entry | residual z-score | caller-set threshold $c$ |
| exit | inside band | or time stop / hard loss stop |
| max hold | caller-set | days to weeks |
| $I$ | caller-set | gross dollars per pair |
| ADV cap | $1\%$ of ADV | per leg |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.pairs_trading` with:

1. `pair_residual(prices_A, prices_B, t1, t2, return_type) -> (R_A, R_B, tilde_A, tilde_B)` — no look-ahead.
2. `open_pair(A, B, I, P_A, P_B, rich) -> (Q_A, Q_B)` — both dollar identities exact before rounding; then round with a cash residual.
3. `blotter(Q, prices, lot) -> list[OrderIntent]` — both legs or neither; never live routing.
4. `pnl(D_A, D_B, fwd_A, fwd_B, costs) -> float`.

Refuse pairs with missing borrow on the rich leg. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Divergence.** Some pairs never come back; the fade is a bet, not an identity. If you do X = drop diverging pairs from the historical sample at the stop date, the backtest lies by keeping only the ones that reverted.
- **News breaks.** A merger, fraud, or earnings print can make $\varepsilon$ a new mean, not a shock. If you do X = hold through a takeout gap because the z-score is large, the backtest lies about a fade that was not there.
- **Correlation breakdown.** Crises lift the common factor and scramble the pair. If you do X = freeze the 12-month correlation from a calm year into a crisis hold, the screen is stale.
- **Double-leg slippage.** Two fills, two opportunities to miss neutrality. If you do X = assume both legs fill at mid, the backtest lies about the dollar-neutral identity you actually got.

## 11. Acceptance tests

- Identity $P_A Q_A + P_B Q_B = 0$ after constructing $Q$, before round.
- Identity $P_A\lvert Q_A\rvert + P_B\lvert Q_B\rvert = I$ before round.
- Swapping labels $A$/$B$ only flips signs.
- $\tilde R_A + \tilde R_B = 0$ to numerical precision.
- Permuting all prices after $t_2$ must not change the $t_2$ residual. If a shuffled future path changes $\tilde R$, the implementation looks ahead and the backtest lies.
- Missing borrow on the rich leg → refuse, do not emit a one-legged blotter. If the blotter contains only the cheap long, the test must fail.
- Adding linear costs $\tau$ weakly decreases P&L. If adding $\tau$ increases P&L, costs are signed wrong and the backtest lies.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
