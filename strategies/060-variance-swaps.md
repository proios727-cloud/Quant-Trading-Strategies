---
rank: 60
slug: variance-swaps
title: "Volatility Trading with Variance Swaps"
asset_class: "volatility / indexes"
style: "pure variance / no delta hedge"
horizon: "Contract tenor $T$ (often 1m–1y)"
instruments: "variance swaps on an index and/or constituents"
---

# 060. Volatility Trading with Variance Swaps

| Field | Value |
|---|---|
| Popularity rank (this kit) | 60 of 101 |
| Why it sits here | The clean vol bet: swap realized variance vs a strike. Used in place of straddles so directional delta-hedging is unnecessary. |
| Aliases | varswap, realized vs implied variance |
| Asset class | volatility / indexes |
| Style | pure variance / no delta hedge |
| Typical horizon | Contract tenor $T$ (often 1m–1y) |
| Instruments | variance swaps on an index and/or constituents |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A variance swap pays realized variance minus a strike, times a variance notional. Long the swap if you expect realized variance above implied (the strike); short if you expect the opposite. No delta hedge is required: the contract is already linear in variance. Dispersion can be done with a short index swap versus long single-name swaps.

You are betting on quadratic variation versus $K$, not on the index level. File 030 can implement VRP with a short straddle; this file is the same economic view without warehouse delta. File 051 is dispersion in listed straddles; the dispersion variant here is the same idea in $v(T)$ units.

Typical users are vol desks that can face OTC variance or a listed proxy. Horizon is the contract tenor, often one month to one year. Size off a designed spike in $v(T)$, not off a vega number that forgets variance convexity. Delay-1: $K$ known before the contract starts. Jumps count; censoring the largest $R(t)^2$ is a different contract.

## 2. First principles

A variance swap is a forward on quadratic variation. Over $T$ trading days the floating leg is realized variance

$$
v(T) = \frac{F}{T}\sum_{t=1}^{T} R(t)^2
$$

built from log returns

$$
R(t)=\ln\frac{S(t)}{S(t-1)}
$$

$F=252$ if $t$ is trading days. The mean of $R$ is **not** subtracted, and the denominator is $T$, not $T-1$: this is quadratic variation, not a sample variance. A two-return path $R=\pm x$ has $v=x^2$ even though the sample variance of demeaned returns is zero. If your function matches a pandas `var(ddof=1)`, it is not this contract.

The swap pays

$$
P(T) = N\bigl(v(T) - K\bigr)
$$

with variance notional $N$ and strike $K$ (in variance units, e.g. $0.20^2$ if vol is 20%). Long $N>0$ if you want realized above implied. Short $N<0$ harvests the variance risk premium when $K$ sits above typical $v(T)$. Using vol points as $K$ without squaring is a units bug that will look like a 0.20 versus 0.04 disagreement.

Unlike a straddle, you do not need to trade the underlying to stay delta-neutral. Convexity in volatility still hurts a short: a spike in $v(T)$ is linear in variance, which is quadratic in vol.

That is the whole contract. Everything below is how to choose the sign, how to mark, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $S(t)$ | underlying level |
| $R(t)$ | log return on bar $t$ |
| $v(T)$ | realized variance over the contract |
| $K$ | variance-swap strike |
| $N$ | variance notional (positive = long variance) |
| $P(T)$ | payoff at expiry |
| $F$ | annualization (252 on trading days) |
| $T$ | number of bars in the contract |
| $\sigma_I,\sigma_i$ | index and single-name implied vols if running dispersion |

## 4. Mathematics

### 4.1 Realized variance

On the contract window, using the official observation calendar:

$$
v(T) = \frac{F}{T}\sum_{t=1}^{T} R(t)^2
$$

Jump days stay in the sum. Dropping a halt day, or replacing a limit-down return with a cap that the contract does not have, restates $v(T)$.

$$
R(t)=\ln\frac{S(t)}{S(t-1)}
$$

$F=252$ if $t$ is trading days. Mean of $R$ is **not** subtracted (denominator $T$, not $T-1$). Simple returns instead of logs are a different floating leg; do not mix them in a test that claims to match a confirmation.

### 4.2 Payoff

$$
P(T) = N\bigl(v(T) - K\bigr)
$$

$N$ is variance notional. Vega notional is $N_{\mathrm{vega}}=2N\sqrt{K}$ if you convert; size in this file is $N$. A short is $N<0$. Costs and any contractual cap on $v(T)$ sit outside this line and must still enter P&L. An uncapped model on a capped contract will overstate short-variance losses on a spike.

### 4.3 Sign and dispersion

Compare $K$ (implied variance) to a trailing realized $v$ that **ends before** the start of the new contract, or to a VRP proxy as in 030. Short variance if implied is rich; long if cheap.

Dispersion: short index variance, long constituent variance with notionals matching index weights, analogous to 051 but in $v(T)$ units rather than straddles. The entry decision uses data before the contract starts. Realized $v(T)$ over the life is the outcome, not the gate.

### 4.4 Mark-to-market

Before expiry, mark with expected remaining variance plus realized so far, or with a replicating strip of listed options if you warehouse. P&L from fill to $T$ is $P(T)$ minus entry mark minus costs. Report $P(T)/N$, realized versus $K$, and jump days. A warehouse delta hedge of the log-strip is implementation of $P(T)$, not a change in the identity.

## 5. Step-by-step algorithm

1. **Underlier.** Index (default) and/or constituents for dispersion. This step exists so a single-name variance swap is not silently substituted for index VRP.
2. **Strike.** $K$ from the variance-swap curve (or from a listed proxy such as vol futures converted to variance) dated $\le t$. Converting vol to variance requires a square. VIX futures basis (file 031) is not $K$ unless documented as a proxy.
3. **Sign.** Short $N<0$ if $K$ is rich versus the pre-contract realized proxy; long otherwise; flat inside costs. The proxy window ends before the contract starts.
4. **Size.** Variance notional $N$ so a designed spike in $v(T)$ fits $L_{\max}$. Vega notional that ignores variance convexity will understate short risk.
5. **Blotter.** OTC swap or listed proxy. Emit intents. Do not route live orders.
6. **Observe.** Accrue $R(t)^2$ on the official calendar. Do not drop jump days. A missing close is a contract term, not a license to interpolate.
7. **Settle.** Pay $P(T)=N(v(T)-K)$ at $T$. Apply the cap if the confirmation has one.
8. **Warehouse (optional).** If you replicate, hold the log-strip of options and delta-hedge that strip; that is implementation, not a change in $P(T)$.

## 6. Execution protocol

- Default entry: next close after $K$ is known. Delay-0 is research-only.
- OTC or listed vol futures as a proxy. Mark with a variance-swap replicating portfolio of options if you must warehouse.
- Jumps count. Censoring the largest $R(t)^2$ is not this contract.

## 7. Data contract

Required, point-in-time:

- Underlying levels on the swap observation calendar
- Variance-swap strike $K$ (or option strip used to imply $K$)
- Contract terms: $T$, $F$, observation day-count, cap if any
- For dispersion: constituent weights and single-name $K_i$

Not used by this spec: equity book value, earnings, SUE, VIX futures basis as a substitute for $K$ unless documented as a proxy.

No look-ahead on $S(t)$ inside $v(T)$ when making the entry decision (the decision uses data before the contract starts). Using in-contract realized variance to decide the sign is peeking at $P(T)$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor | 1m–1y | caller-set $T$ |
| $F$ | 252 | trading-day bars |
| $N$ | caller-set | variance notional |
| $K$ | from the varswap curve | |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.variance_swaps` with:

1. `realized_variance(prices, F) -> float` — $v(T)$ with $\sum R(t)^2$, denominator $T$, mean not subtracted.
2. `payoff(N, v, K) -> float` — $N(v-K)$ to `1e-8`.
3. `sign(K, realized_proxy, costs) -> int` — $\{-1,0,+1\}$, no look-ahead.
4. `blotter(sign, N, terms) -> list[OrderIntent]` — swap or proxy, never live routing.
5. `pnl(N, v, K, costs) -> float` — matches $P(T)$ minus costs.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Variance convexity.** A vol spike hurts shorts more than a similar-vega straddle. Sizing off vega as if the contract were linear in vol is how shorts blow up.
- **Jumps.** Quadratic variation is jump-sensitive by design. Dropping jump days is not this contract.
- **OTC / counterparty.** Unless cleared.
- **Caps.** Some contracts cap $v(T)$; an uncapped model then mis-marks.
- **Units.** $K$ in vol points versus variance units scales P&L by about $1/\sigma$.
- **Look-ahead sign.** Using in-contract $v(t)$ to decide a late entry uses the outcome as the gate.

## 11. Acceptance tests

- Toy: two returns $R=\pm x$, $T=2$, $F=1$ → $v=(x^2+x^2)/2=x^2$, not a demeaned variance of 0.
- Denominator is $T$, not $T-1$.
- $P(T)=N(v-K)$ to `1e-8`.
- Permuting prices after the entry decision must not change the entry sign.
- Adding linear costs $\tau$ weakly decreases P&L.
- A pandas-style sample variance (mean subtracted, `ddof=1`) must not pass `realized_variance`.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
