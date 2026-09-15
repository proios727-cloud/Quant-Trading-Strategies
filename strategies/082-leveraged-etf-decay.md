---
rank: 82
slug: leveraged-etf-decay
title: "Leveraged ETF Decay (Short LETF Pair)"
asset_class: "ETFs"
style: "structural short / volatility drag"
horizon: "Weeks to months; large short-term drawdown risk"
instruments: "2× or 3× LETF, matching inverse LETF, Treasury/cash ETF"
---

# 082. Leveraged ETF Decay (Short LETF Pair)

| Field | Value |
|---|---|
| Popularity rank (this kit) | 82 of 101 |
| Why it sits here | Well-known compounding/decay of daily-reset 2× and 3× products. Short both the levered and inverse levered ETF vs a cash sleeve. |
| Aliases | LETF pair short, volatility drag, compounding decay |
| Asset class | ETFs |
| Style | structural short / volatility drag |
| Typical horizon | Weeks to months; large short-term drawdown risk |
| Instruments | 2× or 3× LETF, matching inverse LETF, Treasury/cash ETF |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

Daily rebalancing of LETFs buys high and sells low, creating negative drift when volatility is high. Short both the levered and inverse products with the same leverage and underlying; park proceeds in T-bills / a Treasury ETF.

You are betting that the product of the two NAV ratios, $\prod(1-L^2 r_t^2)$, decays faster than borrow fees, expense-ratio differences, and the path of a one-sided trend. Daily reset forces both the $+L$ and $-L$ products to trade against themselves in a choppy market. Shorting *both* equal notionals, with cash from the shorts in Treasuries, is the structural expression of that drag.

You are not collecting a free lunch. A violent one-way trend can double one short’s liability before the product identity helps you. You are not shorting a $3\times$ against a $2\times$ inverse: $L$ must match. You are not holding a one-legged short if one locate fails. You are not earning the prospectus $L r$; you earn traded LETF returns minus borrow.

Typical users are volatility-drag research books and structural-short overlays that can warehouse crash risk. Horizon is weeks to months, with large short-term drawdown risk. Rebalance weekly or when notionals drift 10%. Hard flatten in the simulator if one short explodes. Delay-1; no live routing.

## 2. First principles

A $L\times$ daily LETF targeting index simple return $r_t$ has NAV (ignoring fees)

$$
V_{t+1} = V_t\,(1 + L r_{t+1})
$$

This is the daily reset map. Tomorrow’s NAV is yesterday’s NAV times one plus leverage times the *next* index return. Fees and tracking error sit outside this map. Using a weekly return in place of $r_{t+1}$ is a different product than a daily-reset LETF.

Over $n$ days the compounded NAV is a **product**, not $1+L\sum r$:

$$
\frac{V_n}{V_0} = \prod_{t=1}^{n}(1+L r_t)
$$

Compounding is multiplicative. $1+L\sum r$ would be a leveraged *buy-and-hold* index, which these products are not. Variance drag appears because the product of $(1+L r_t)$ is not the leveraged sum. Path matters: two days $+x,-x$ already shrink the product relative to a flat index.

The matching $-L$ inverse product compounds

$$
\frac{V_n^{-}}{V_0^{-}} = \prod_{t=1}^{n}(1-L r_t)
$$

Same reset, opposite leverage. A one-way rally explodes $V$ and crushes $V^{-}$; a one-way crash does the reverse. Shorting only one of them is an outright leveraged bet, not this spec.

The product of the two NAV ratios is

$$
\frac{V_n}{V_0}\cdot\frac{V_n^{-}}{V_0^{-}} = \prod_{t=1}^{n}\bigl(1-L^2 r_t^2\bigr)
$$

Every nonzero $r_t$ makes a factor $1-L^2 r_t^2<1$. That is the volatility drag. It is an identity on the *index path* under perfect tracking, not a guaranteed P&L on traded ETFs. Shorting **both** notionals equally, and holding cash with the proceeds, is a bet that this product decays faster than fees, borrow, and the path of a one-sided trend (which can make one short explode before the product identity helps you).

That is the whole strategy. Everything below is the 1:1 notional pair, the cash sleeve, and how not to look ahead.

## 3. Notation

| Symbol | Definition |
|---|---|
| $L$ | daily leverage, $2$ or $3$ |
| $r_t$ | underlying index simple return |
| $V, V^{-}$ | NAV of the $+L$ and $-L$ products |
| $D_{+}, D_{-}$ | signed dollar holdings; both negative in this spec |
| $D_{\mathrm{cash}}$ | Treasury / T-bill ETF holding, $D_{\mathrm{cash}}>0$ |
| $I$ | gross short notional $\lvert D_{+}\rvert+\lvert D_{-}\rvert$ |
| $\delta$ | notional drift trigger for a rebalance (default $10\%$) |

Hedge ratio starts at 1:1 notionals: $\lvert D_{+}\rvert=\lvert D_{-}\rvert$. Rebalance when they drift.

## 4. Mathematics

### 4.1 Daily reset identity

Keep the one-step NAV map

$$
V_{t+1} = V_t\,(1 + L r_{t+1})
$$

Keep that one-step map together with the $n$-day product above. This is the diagnostic on the index, not the traded P&L. Fees, expense ratios, and tracking error versus the prospectus sit outside this identity; they usually add to decay but can go the other way. If you P&L this map instead of traded $R_{\pm}$, you have ignored borrow, spreads, and tracking.

### 4.2 Pair holdings

Short the $L\times$ long ETF and short the $L\times$ inverse ETF, equal notional at entry:

$$
D_{+} = -\frac{I}{2},\qquad D_{-} = -\frac{I}{2},\qquad D_{\mathrm{cash}} = I
$$

Both LETF weights are negative. Cash from the shorts sits in a Treasury ETF (or T-bills). The book is dollar-flat at entry ($D_{+}+D_{-}+D_{\mathrm{cash}}=0$) and short two LETFs. If either locate is missing, emit nothing: a one-legged short is an outright.

Rebalance when $\lvert\lvert D_{+}\rvert-\lvert D_{-}\rvert\rvert / (I/2) > \delta$, or on a calendar (weekly default). Reset to 1:1 notionals. Drift happens because one leg’s price path outruns the other. Skipping rebalance after a trend leaves you over-short the winner.

### 4.3 Holding-period P&L

$$
\mathrm{P\&L} = D_{+} R_{+}^{\mathrm{fwd}} + D_{-} R_{-}^{\mathrm{fwd}} + D_{\mathrm{cash}} R_{\mathrm{cash}}^{\mathrm{fwd}} - \mathrm{borrow} - \mathrm{costs}
$$

$R_{+}^{\mathrm{fwd}}$ and $R_{-}^{\mathrm{fwd}}$ are traded LETF simple returns, not the prospectus $L r$. Borrow on **both** shorts is first-class, not an afterthought. Raising borrow fees must weakly decrease P&L. Report path-wise drawdown; a mean decay with a $50\%$ hole is still a failed book. If you omit the cash sleeve’s return, you understate income and hide that the book is dollar-flat at reset.

## 5. Step-by-step algorithm

1. **Pair.** Pick an underlying, $L\in\{2,3\}$, the listed $+L$ ETF and the listed $-L$ ETF, plus a Treasury ETF. This step exists so $L$ matches and the cash sleeve is explicit. A $3\times$ versus $2\times$ pair is not this identity.
2. **Borrow.** Enter only if locate exists on **both** shorts. If either fails, do not put on a one-legged short. This step exists because a missing locate is an outright leveraged short.
3. **Size.** $D_{+}=D_{-}=-I/2$, $D_{\mathrm{cash}}=I$. This step exists to start dollar-flat and 1:1.
4. **Filter (optional).** Skip entry if realized vol of the underlying is below a floor (decay is small) or above a crash cap (one-leg blow-up risk). Default: no filter. This step exists as risk control, not as a second alpha. Vol must end before entry.
5. **Hold.** Weeks to months. Watch notional drift daily. This step exists because the identity is path-dependent; ignoring drift lets one short dominate.
6. **Rebalance.** Weekly, or when drift $>10\%$. This step exists to restore 1:1 before the book becomes a directional LETF short.
7. **Stops.** A violent trend that doubles one short’s liability is a hard flatten in the simulator. There is no “the identity will save us.” This step exists because the product identity does not cap one-leg losses.
8. **Blotter.** Intents only. Never live routing. This step exists because this is a research short with crash risk, not a live router.

## 6. Execution protocol

- Enter only when borrow is available on both names. Model borrow fees explicitly. If you do $X$ = assume zero borrow, the backtest lies in every hard-to-borrow inverse LETF.
- Hard stops: a violent trend makes one short explode even if the pair “should” decay.
- Do not short a $3\times$ against a $2\times$ inverse. $L$ must match.

## 7. Data contract

Required, point-in-time:

- Adjusted prices for $+L$, $-L$, and the cash ETF
- Underlying index returns for the diagnostic product identity
- Borrow availability and fees on both shorts
- ADV / AUM; some inverse LETFs are thin
- Prospectus leverage $L$ and reset convention (daily)

Not used by this spec: Fama–French factors, IBS, NAV arb between SPY and IVV.

If you do $X$ = use index $L r$ as the LETF return, you ignored tracking error. If you do $X$ = use a weekly-reset map on a daily-reset product, the product identity is the wrong one. If you do $X$ = peek at next week’s borrow fee to decide whether to enter, you looked ahead. Locate and fees as of $t$; no restatement of prospectus $L$.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| $L$ | $2$ or $3$ | must match both legs |
| rebalance | weekly or $10\%$ drift | whichever first |
| cash sleeve | Treasury ETF | proceeds of shorts |
| vol filter | off | optional risk-off |
| delay | 1 bar | |

## 9. Agent implementation contract

Build a Python module `strategies.leveraged_etf_decay` with:

1. `nav_product(r, L) -> float` — $\prod_t(1-L^2 r_t^2)$ as a diagnostic on the index path.
2. `weights(I, prices) -> dict` — $D_{+},D_{-},D_{\mathrm{cash}}$ with $\lvert D_{+}\rvert=\lvert D_{-}\rvert=I/2$ at reset.
3. `rebalance(D, prices, delta) -> dict` — restore 1:1 if drift $>\delta$.
4. `blotter(D, prices, lot, borrow) -> list[OrderIntent]` — refuse if either short has no locate; never live routing.
5. `pnl(D, forward_returns, borrow_fees, costs) -> float` — matches §4.3.

Refuse venue exploits, spoofing, or unauthorized access. This is a structural short with crash risk, not a free lunch.

## 10. Risks and failure modes

- **Path-dependent blow-up.** One leg trends; the short on that leg explodes. The product identity does not cap that loss on a finite horizon.
- **Borrow recalls.** Losing one locate leaves a naked short LETF.
- **Tracking error.** Traded $R_{\pm}$ is not $L r$.
- **Product shutdown / regulatory halt.** Inverse and levered products get restricted.

## 11. Acceptance tests

- Two-day path $r=(+x,-x)$: $\prod(1-L^2 r_t^2)<1$ for $x\neq 0$.
- At reset, $D_{+}+D_{-}+D_{\mathrm{cash}}=0$ and $\lvert D_{+}\rvert=\lvert D_{-}\rvert$.
- Missing locate on one name → no blotter (empty intents), not a one-leg short.
- P&L includes borrow: raising borrow fees weakly decreases P&L.
- Permuting future LETF prices must not change today’s target $D$.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
