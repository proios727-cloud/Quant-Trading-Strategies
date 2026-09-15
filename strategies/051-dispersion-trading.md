---
rank: 51
slug: dispersion-trading
title: "Dispersion Trading in Equity Indexes"
asset_class: "volatility / indexes"
style: "short index vol / long constituent vol"
horizon: "~1-month straddles held to expiry"
instruments: "near-ATM index straddle short; near-ATM single-stock straddles long"
---

# 051. Dispersion Trading in Equity Indexes

| Field | Value |
|---|---|
| Popularity rank (this kit) | 51 of 101 |
| Why it sits here | The standard correlation-risk premium trade: index implied vol is usually rich vs a basket of single-stock options. |
| Aliases | correlation trade, index vs single-stock vol |
| Asset class | volatility / indexes |
| Style | short index vol / long constituent vol |
| Typical horizon | ~1-month straddles held to expiry |
| Instruments | near-ATM index straddle short; near-ATM single-stock straddles long |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Index variance is a weighted sum of constituent variances plus covariances. Index options typically price that covariance piece rich versus realized (and versus a basket of single-stock implieds). Long near-ATM single-stock straddles, short a matching near-ATM index straddle. You are short implied correlation.

Reverse the book if implied index vol is cheap versus the theoretical basket. You are not making a directional index bet if notionals match, and you are not harvesting single-name VRP in isolation: the longs exist to offset the diagonal of the variance identity. File 030 sells index vol outright; this file sells the correlation residual.

Typical users are vol RV desks that can trade a package of listed index and single-stock options. Horizon is about one month to expiry. Open as a package; do not leg the short index first. Line-item costs on a hundred names can eat the premium, which is why the PCA subset exists.

A crash that sends $\rho_{ij}\to 1$ is the structural risk: short index vol loses more than the long names make. Size off that path, not off the credit.

## 2. First principles

Let $w_i$ be index weights and $R_I=\sum_i w_i R_i$. Index variance expands as

$$
\sigma_I^2 = \sum_{i,j} w_i w_j \sigma_i \sigma_j \rho_{ij}
$$

The diagonal $i=j$ is weighted constituent variance. The off-diagonal is correlation. If every $\rho_{ij}=1$ and every $\sigma_i$ is equal, $\sigma_I$ equals that common $\sigma$: there is no diversification. If correlations are zero, $\sigma_I$ is much smaller than the typical single-name $\sigma_i$. Index options that price $\sigma_I$ as if correlations were high are selling that diversification short.

A short index straddle versus long constituent straddles, notionally matched, is approximately short the off-diagonal: you collect the correlation premium if $\rho_{ij}$ implied exceeds $\rho_{ij}$ realized. The match is in vega or in straddle notional, not in share count by accident. Theoretical index vol from constituent implieds $\sigma_i$ and a correlation matrix $\rho_{ij}$ is the right-hand side above. Compare it to listed index implied $\sigma_I^{\mathrm{mkt}}$. If $\sigma_I^{\mathrm{mkt}}$ is rich, sell the index straddle and buy the stock straddles.

That is the whole trade. Everything below is share counts, the PCA subset, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $\sigma_I$ | theoretical index vol from the basket identity |
| $\sigma_I^{\mathrm{mkt}}$ | listed index implied vol |
| $\sigma_i$ | implied vol of constituent $i$ |
| $w_i$ | index weights, $\sum_i w_i=1$ |
| $\rho_{ij}$ | sample (or factor) return correlations |
| $\psi_{ij}$ | statistical-factor correlation (PCA variant) |
| $\xi_i$ | specific-risk fraction in the factor variant |
| $n_i$ | share count of name $i$ in the replicating basket |
| $P_i, P_I$ | stock price and index level |
| $S_i$ | shares outstanding (cap-weight input) |
| $N^\ast$ | subset size in the PCA variant |
| $C_{\mathrm{idx}}, C_i$ | straddle credits (index short, names long) |

## 4. Mathematics

### 4.1 Theoretical index vol

Using constituent implieds and a correlation matrix dated $\le t$:

$$
\sigma_I^2 = \sum_{i,j} w_i w_j \sigma_i \sigma_j \rho_{ij}
$$

$\rho_{ij}$ must be estimated on a window that ends at $t$, never on the holding period. Using realized correlation over the option’s life to decide the gate is look-ahead. Sample $\rho$ on 500 names is singular and unstable; the factor $\psi$ variant is the default research book. Gate:

- $\sigma_I^{\mathrm{mkt}} > \sigma_I$ — index vol rich → **short** index straddle, **long** stock straddles
- $\sigma_I^{\mathrm{mkt}} < \sigma_I$ — reverse the book
- inside a cost band — flat

The cost band has to include one index line plus every name line you actually trade. A gate that only charges the index bid/ask will always look open.

### 4.2 Share counts (cap-weighted example)

Match the index straddle notional to the cash basket. One cap-weighted construction uses shares outstanding $S_i$:

$$
n_i = \frac{S_i P_I}{\sum_j S_j P_j}
$$

These $n_i$ are the cash-index replicating shares, not option lots yet. If $S_i$ is stale, mega-caps will be mis-weighted and the “index” short will not match the longs. The index level is recovered as

$$
P_I = \sum_i n_i P_i
$$

If this recovery fails, the share-count formula and the published index are not the same object. Hold ~1 month to expiry. Scale the short index contracts so vega (or straddle notional) matches $\sum_i n_i$ times the stock-straddle multipliers. Skip names without listed options. Filling missing vols with zero (or with $\sigma_I$) silently changes $\sigma_I$ and the basket.

### 4.3 Subset / PCA variant

Replace $\rho_{ij}$ by a statistical-factor correlation $\psi_{ij}$. Specific-risk contribution of name $i$ is $w_i^2\sigma_i^2\xi_i^2$. Long only the $N^\ast$ names with the **smallest** specific-risk contributions (default $N^\ast=100$ in S&P 500). The correlation matrix on 500 names is singular and unstable; the factor $\psi$ variant is the default research book. Smallest specific risk means the names that contribute most to the index’s systematic variance, which is the piece you are trying to offset. Longing the noisiest names would add idiosyncratic straddles you did not intend.

### 4.4 Holding-period P&L

Mark each straddle to mid from fill to expiry (or unwind), plus financing, minus costs:

$$
\mathrm{P\&L} = -f_T^{\mathrm{idx}} + \sum_i f_T^{(i)} - \mathrm{costs}
$$

where each $f_T$ is the straddle terminal identity $-(S_T-K)_+-(K-S_T)_+$ plus the signed premium. The index term is short, so it enters with a minus on a long-straddle $f_T$ convention, or use a short-straddle identity on that leg and keep the sign consistent in code. Report P&L, implied-versus-realized correlation, and turnover of the option lines. Package P&L is the object; a test that only checks the index leg is not this spec.

## 5. Step-by-step algorithm

1. **Index.** Point-in-time constituents and weights (default S&P 500). Drop names that halt or delist before expiry; do not backfill. This step exists so today’s reconstitution does not leak into last month’s basket.
2. **Implieds.** Near-ATM listed vols for the index and for each name, same tenor (~1m). If ATM is missing, use the nearest OTM. Mixing a 1-month index vol with 3-month single-name vols makes $\sigma_I$ incomparable to $\sigma_I^{\mathrm{mkt}}$.
3. **Correlations.** Sample $\rho$ or factor $\psi$ on a window ending at $t$, never on the holding window. Holding-window $\rho$ is realized correlation, which is the outcome of the trade, not the gate.
4. **Gate.** Compare $\sigma_I^{\mathrm{mkt}}$ to $\sigma_I$. Inside costs → flat. Flat is valid. Forcing a small dispersion book every month ignores line-item costs.
5. **Basket.** Full listed-option universe, or the $N^\ast$ PCA subset. Skip names without chains. Skipping must remove those weights from the match, not leave a hole versus the index short.
6. **Size.** Share counts $n_i$ as in 4.2; match index notional. Cap by option ADV / open interest. Caps that drop names require a rebuild of the index short, not a leftover naked index straddle.
7. **Blotter.** Short index straddle, long name straddles (or the reverse). Round lots, emit intents. Do not route live orders. Emit as one package timestamp so tests can forbid legging.
8. **Hold.** Open as a package; expire or unwind together. Delay-1: chains known today trade the next close. Unwinding names into earnings while keeping the index short is a different spec.

## 6. Execution protocol

- Default fill: next close after implieds and $\rho$ are known. Delay-0 is research-only.
- Open as a package; do not leg the short index first and leave the longs unfilled. A one-sided fill is short index vol, file 030, not dispersion.
- Correlation matrix is singular and unstable — prefer the factor $\psi$ variant.
- Reverse the book if implied index vol is cheap versus theory.

## 7. Data contract

Required, point-in-time:

- Index composition and weights dated $\le t$
- Listed option chains for the index and constituents (strike, expiry, bid/ask, OI)
- Prices $P_i$, index level $P_I$, shares outstanding if using 4.2
- Return history for $\rho_{ij}$ or factor $\psi_{ij}$, window ending at $t$

Not used by this spec: book value, earnings, SUE, VIX futures basis as a trading signal (VIX may proxy $\sigma_I^{\mathrm{mkt}}$ only).

No restatement of index weights after $t$. Delisted names stay until the delist date. Earnings dates may be used as a hold-or-skip filter if documented; they are not an input to $\sigma_I$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor | 1 month | hold to expiry |
| $N^\ast$ | 100 | S&P 500 PCA subset |
| PCA factors | via eRank | $K$ factors |
| strike | near ATM | OTM-near-ATM if ATM missing |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.dispersion_trading` with:

1. `theoretical_vol(weights, sigmas, rho) -> float` — $\sigma_I$ from the basket identity, no look-ahead.
2. `share_counts(S, P, P_I) -> pd.Series` — $n_i$ matching 4.2.
3. `subset(weights, sigmas, xi, N_star) -> list` — smallest specific-risk names.
4. `blotter(gate, n, chains, lot) -> list[OrderIntent]` — index short and name longs (or reverse), never live routing.
5. `pnl(index_leg, name_legs, costs) -> float` — package P&L.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Correlation spike.** In a crash, $\rho_{ij}\to 1$ and short index vol loses more than the long names make. That is the premium you sold. Size off a 2008-like correlation path.
- **Unstable $\rho_{ij}$.** Sample correlation on $N=500$ is not a tradable object; use $\psi$. A monthly inverted $\rho$ will flip the gate on noise.
- **Line-item costs.** One hundred option lines eat the premium. A mid-to-mid backtest will overstate the edge by exactly those spreads.
- **Reverse-dispersion regimes.** Cheap index vol vs theory flips the sign. Ignoring the reverse gate leaves you short correlation when it is already cheap.
- **Incomplete chains.** Dropping names without rebuilding the index short leaves a naked index short.
- **Legging.** Filling the index first is a directional short-vol interval you did not size.

## 11. Acceptance tests

- Two-name toy: $w=(1/2,1/2)$, $\rho_{12}=1$, $\sigma_1=\sigma_2=\sigma$ → $\sigma_I=\sigma$.
- Same toy with $\rho_{12}=0$ → $\sigma_I=\sigma/\sqrt{2}$.
- $n_i$ identity: $P_I=\sum_i n_i P_i$ to `1e-8` on the cap-weighted construction.
- Permuting chains and returns after $t$ must not change $\sigma_I$ or $n_i$ at $t$.
- Names without listed options are dropped, not filled with zero vol.
- Adding linear costs $\tau$ weakly decreases P&L.
- Using holding-period realized $\rho$ in the $t$ gate must fail the look-ahead test.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
