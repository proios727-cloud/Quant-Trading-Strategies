---
rank: 98
slug: crypto-ann
title: "Cryptocurrency ANN Directional Forecast"
asset_class: "cryptocurrencies"
style: "supervised neural net on technical features"
horizon: "Intraday to daily bars (example: 15-minute BTC)"
instruments: "BTC (or liquid crypto) spot or perpetual"
---

# 098. Cryptocurrency ANN Directional Forecast

| Field | Value |
|---|---|
| Popularity rank (this kit) | 98 of 101 |
| Why it sits here | Representative ML crypto overlay: technical features into an ANN that predicts return quantiles (Nakano–Takahashi style). |
| Aliases | crypto neural net, BTC ANN, quantile-softmax directional net |
| Asset class | cryptocurrencies |
| Style | supervised neural net on technical features |
| Typical horizon | Intraday to daily bars (example: 15-minute BTC) |
| Instruments | BTC (or liquid crypto) spot or perpetual |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Build technical features from normalised returns, exponential moving averages, exponential moving standard deviations, and RSI. Train a feed-forward net with ReLU hidden layers and a softmax over return quantiles. Trade only when the predicted mass sits on an extreme quantile: buy the top bin, sell the bottom bin, otherwise flat.

You are betting that a walk-forward net, trained only on already-closed bars, has a one-bar edge in the extreme quantiles after fees, spread, and perp funding. You are not valuing BTC from supply, hash rate, or a discounted cash flow. You are not trading interior quantiles, and you are not using the same bar’s close both as a feature and as a fill. Transaction costs dominate 15-minute trading; a softmax that is confident in $p_K$ is not a reason to ignore the fee schedule.

Architecture, $\tau$, $T_1$, and $K$ are frozen before the test window. Walk-forward only: train on a past window, predict the next bar, then shift. Refitting on the bar you trade, or letting quantile edges see the test return, is a different and invalid book. Crypto weekends still require a closed bar; do not fill gaps with zeros.

Hyperparameter search belongs inside the training window, not on test Sharpe. A net that was widened because last week’s test loss looked high has already seen the test. The same rule applies to picking which $\tau$ grid “works”: freeze it, or nest a validation slice that still ends before the bar you trade. Delay-0 using the same-bar close as a feature and as a fill is research-only; live books wait for the next open.

## 2. First principles

Index bars so that $t=0$ is the latest closed bar and $t$ increases into the past. The one-bar simple return that uses only already-closed prices is

$$
R(t) = P(t)/P(t+1) - 1
$$

$P(t)$ is the close of bar $t$; $P(t+1)$ is the previous close under this indexing. The next bar’s return is not in this formula and must not enter $X^{(0)}$. Demean and vol-normalise $R$ over a window of $T_1$ bars that ends at the feature time (never into the future). Those normalised returns, plus EMAs, EMSDs, and RSI at several spans $\tau$, are the inputs $X^{(0)}$.

An EMA on a series $x$ uses decay $\lambda$ on the previous EMA and weight $1-\lambda$ on the new print. The optional smoothing in this spec is the standard EMA decay

$$
\lambda = (\tau-1)/(\tau+1)
$$

$\tau$ is a span in bars (or a documented translation from clock time on a 15-minute grid). This $\lambda$ is a hyperparameter identity, not something estimated on the test set. A different decay is a different feature; freeze it before the test window.

so

$$
\mathrm{EMA}_{\tau}(t) = \lambda\,\mathrm{EMA}_{\tau}(t+1) + (1-\lambda)\,x(t)
$$

(again $t+1$ is the previous bar under the $t=0$ latest convention). The recursion is causal: the EMA at $t$ may use $x(t)$ and older EMAs, never $x$ from a bar that has not closed. Seed the EMA on a burn-in that is also in-sample relative to the feature time; a seed that uses the whole series including the future is look-ahead. EMSD is the same smoother on squared deviations from the EMA. RSI is the usual 0–100 transform of average gains versus average losses over $\tau$.

Labels are a one-hot quantile of the **next** bar’s return, known only after that bar closes. On the training set, $K$ bins give a one-hot vector

$$
S_{\alpha}(t) \in \{0,1\}^{K}
$$

Exactly one coordinate is 1: the quantile bin of the forward return used as the label. Live trading does not observe $S_{\alpha}$ for the bar you are about to trade; the net outputs $p_{\alpha}$ instead. Quantile edges are estimated on a window that ends **before** the label bar.

and the bins on that bar sum to one:

$$
\sum_{\alpha=1}^{K} S_{\alpha}(t) = 1
$$

This is a one-hot constraint, not a softmax. If a training row has no label (missing next bar), drop the row; do not put mass on every bin. Ties on a quantile edge go to a documented rule and stay frozen.

The network is an affine map at each layer $\ell$:

$$
Y^{(\ell)} = A^{(\ell)} X^{(\ell-1)} + B^{(\ell)}
$$

$X^{(0)}$ is the feature vector from causal technicals. $A^{(\ell)}$ and $B^{(\ell)}$ are frozen after the training window; they are not updated on the bar you trade. Width and depth are hyperparameters, not objects that grow when the test loss looks bad.

then a nonlinearity on that pre-activation:

$$
X^{(\ell)} = h^{(\ell)}(Y^{(\ell)})
$$

Hidden layers use ReLU. The output layer uses softmax so the predicted quantile probabilities sum to one:

$$
\sum_{\alpha} p_{\alpha} = 1
$$

Softmax is the live object: $p_{\alpha}\ge 0$ and the sum is 1 to numerical tolerance. Train by cross-entropy versus $S_{\alpha}$, with SGD (or a documented sibling). After training, the live rule is extreme-only:

- buy iff $\max_{\alpha} p_{\alpha} = p_{K}$ (top quantile)
- sell iff $\max_{\alpha} p_{\alpha} = p_{1}$ (bottom quantile)
- otherwise flat

Interior mass, including a confident $p_3$ when $K=5$, is a non-trade. A tie for the max is also a non-trade. That filter exists because costs eat small edges; it is not a claim that interior bins have zero information.

That is the whole strategy. Everything below is how to freeze the architecture, how to walk forward, and how not to leak the next bar into $X^{(0)}$.

## 3. Notation

| Symbol | Definition |
|---|---|
| $P(t)$ | coin price at the close of bar $t$ ($t=0$ latest closed) |
| $R(t)$ | $P(t)/P(t+1)-1$ |
| $T_1$ | normalisation window for demean/vol |
| $\tau$ | EMA / EMSD / RSI span |
| $\lambda = (\tau-1)/(\tau+1)$ | optional EMA decay |
| $X^{(\ell)}$ | activation at layer $\ell$; $X^{(0)}$ is the feature vector |
| $A^{(\ell)}, B^{(\ell)}$ | weights and bias of layer $\ell$ |
| $h^{(\ell)}$ | ReLU on hidden layers; softmax on the output |
| $K$ | number of return quantiles |
| $S_{\alpha}(t)$ | one-hot quantile label |
| $p_{\alpha}$ | softmax probability of quantile $\alpha$ |
| $I$ | absolute dollars (long or short, not both) |

## 4. Mathematics

### 4.1 Features

Return $R(t)=P(t)/P(t+1)-1$, then demean/vol-normalise over window $T_1$. Features: EMA, EMSD, RSI with several $\tau$. Example hyperparameter grid (not magic): EMAs at 30m/1h/3h/6h and RSI at 3h/6h/12h on a 15-minute bar. Every smoother must be causal: no print after the feature timestamp. Permuting prices after the feature bar must leave $X^{(0)}$ unchanged. Volume features are allowed only if documented; this spec’s default $X^{(0)}$ is price-based.

### 4.2 Quantile labels

On the training set only, assign $S_{\alpha}(t)$ from the distribution of $R$ on a window that ends **before** the label bar. The live net must not recompute quantile edges using the test bar. Labels are the **next** bar’s return, not the bar that produced $X^{(0)}$. Contemporaneous labelling is leakage.

### 4.3 Network

The affine pre-activation at layer $\ell$ is

$$
Y^{(\ell)} = A^{(\ell)} X^{(\ell-1)} + B^{(\ell)}
$$

This is a matrix-vector product plus bias, nothing else. Batch-norm, dropout, or recurrent layers are not this spec unless the file is amended. Weights come from the walk-forward training window that ends before the prediction bar.

The activation is

$$
X^{(\ell)} = h^{(\ell)}(Y^{(\ell)})
$$

Hidden: ReLU. Output: softmax so $\sum_{\alpha} p_{\alpha}=1$. Train by cross-entropy; SGD. Walk-forward: after predicting bar $t-1$ (the next one in live time), you may refit using that bar only once it has closed — never before.

### 4.4 Signal and holdings

Buy iff $\max p_{\alpha} = p_{K}$ (top quantile); sell iff $\max p_{\alpha} = p_{1}$. If several $p_{\alpha}$ tie for the max, flatten (do not trade a tie). Position:

$$
D = \begin{cases} +I & \max p_{\alpha} = p_{K} \\ -I & \max p_{\alpha} = p_{1} \\ 0 & \text{otherwise} \end{cases}
$$

$I$ is absolute dollars, long or short, not both. Optional: scale $I$ by a trailing coin-vol target, still using only closed bars. Cap by ADV / book depth. Interior argmax $\Rightarrow D=0$ even if $\max p_{\alpha}$ is 0.99.

### 4.5 Holding-period P&L

Let $R^{\mathrm{fwd}}$ be the simple return from fill to next rebalance (spot or perpetual, including funding if a perp):

$$
\mathrm{P\&L} = D\, R^{\mathrm{fwd}} - \mathrm{costs} - \mathrm{funding}
$$

Fill is the next bar’s open (or delay-1 close). Features at decision $t$ use only bars already closed, so $R^{\mathrm{fwd}}$ is not inside $X^{(0)}$. Report net return on $\lvert D \rvert$, Sharpe on non-overlapping bar returns, and turnover. Costs dominate 15-minute bars; if costs exceed a threshold, flatten rather than churn.

## 5. Step-by-step algorithm

1. **Series.** Liquid BTC (or specified coin) spot or perpetual, bar size documented. Drop halted or missing bars; do not fill with zeros. This step exists so the net cannot treat a hole as a zero return.
2. **Features.** From bars $\ge t$ in the $t=0$ latest convention, build normalised $R$, EMAs, EMSDs, RSI. Freeze $\tau$ and $T_1$ before the test window. This step exists to keep $X^{(0)}$ causal.
3. **Walk-forward.** Train on a past window. Predict the next bar. Then shift the window. Never refit on the bar you trade. This step exists so test P&L is out of sample, not a fit to the same bar.
4. **Softmax.** Read $p_{\alpha}$. Trade only if the argmax is $p_{K}$ (long) or $p_{1}$ (short). This step exists to skip interior bins where costs dominate any leftover edge.
5. **Size.** $\lvert D \rvert = I$, or a vol target on trailing coin vol. Cap by ADV / book depth. This step exists so a confident softmax cannot size through the book.
6. **Blotter.** Spot or perp intent. Lot residual to cash. Do not route live orders. This step exists to keep the research contract off the venue.
7. **Costs.** Subtract fees, spread, and perp funding. If costs exceed a threshold, flatten rather than churn. This step exists because 15-minute BTC without costs is a different, fictional strategy.

## 6. Execution protocol

- Walk-forward: train on past, predict next bar, then shift. Transaction costs dominate 15-minute trading.
- Fill at the next bar’s open (or close, if delay-1 close-to-close is the research choice). Features at decision $t$ use only bars already closed.
- Freeze architecture (depth, width, $K$, $\tau$) before the test window. No look-ahead in EMAs/RSI.
- Do not use the same-bar close as both a feature and a fill (delay-0). That is research-only.

## 7. Data contract

Required, point-in-time, timestamped on **closed** bars only:

- OHLCV (this spec uses close $P(t)$; if you add volume features, document them)
- Perpetual funding prints if the instrument is a perp
- Fee schedule and a spread assumption
- Bar calendar (weekend crypto trades; still require a closed bar)

Look-ahead that invalidates a historical blotter: a future print inside an EMA, quantile edges estimated on the test bar, funding known only after the hold, or zero-filling a missing bar that would have been a drop. Architecture search on the test window is look-ahead even if each forward pass looks causal.

Not used by this spec: equities, CPI, tweet text.

No future bar in $X^{(0)}$. Quantile edges for labels are training-only.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| bar | 15-minute BTC example | caller-set |
| $K$ | 5 quantiles | extreme bins are 1 and $K$ |
| hidden | ReLU, width/depth caller-set | freeze before test |
| $\lambda$ | $(\tau-1)/(\tau+1)$ | optional EMA smoothing |
| $\tau$ grid | 30m/1h/3h/6h EMA; 3h/6h/12h RSI | hyperparameters |
| $T_1$ | caller-set | demean/vol window |
| delay | 1 bar | delay-0 with the same-bar close is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.crypto_ann` with:

1. `features(prices, taus, T1) -> np.ndarray` — $X^{(0)}$, causal EMAs/RSI, no look-ahead.
2. `forward(X0, weights) -> np.ndarray` — softmax $p_{\alpha}$, $\sum p_{\alpha} = 1$ to `1e-8`.
3. `signal(p) -> int` — $+1$ iff argmax is $K$, $-1$ iff argmax is $1$, else $0$; ties $\to 0$.
4. `blotter(signal, I, px, lot) -> list[OrderIntent]` — single-name intent, never live routing.
5. `pnl(D, forward_return, costs, funding) -> float` — matches $D R^{\mathrm{fwd}} - \mathrm{costs} - \mathrm{funding}$.

Walk-forward only. Freeze architecture before the test window. No look-ahead in EMAs/RSI. Not investment advice; crypto is highly speculative. Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Overfit.** A wide net on a single coin memorizes noise.
- **Regime shifts.** Vol and microstructure change; the softmax still outputs a confident $p_{K}$.
- **Exchange outages and funding.** Perps charge funding; spots halt.
- **Not a fundamental value model.** There is no anchor besides lagged technicals.

## 11. Acceptance tests

- Causal EMA: permuting $P$ after the feature bar must not change $X^{(0)}$ at that bar.
- Softmax: $\sum_{\alpha} p_{\alpha} = 1$ to $10^{-8}$; each $p_{\alpha} \ge 0$.
- Interior argmax ($1 < \alpha < K$) $\Rightarrow$ $D = 0$.
- Tie for $\max p_{\alpha}$ $\Rightarrow$ $D = 0$.
- One-bar toy path: $D = I$, $R^{\mathrm{fwd}} = r$ $\Rightarrow$ P&L $= I r - \mathrm{costs} - \mathrm{funding}$ to $10^{-8}$.
- Adding linear costs $\tau$ weakly decreases P&L.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
