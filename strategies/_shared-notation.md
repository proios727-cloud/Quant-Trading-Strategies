# Shared notation

Common dictionary for the 101 strategy files. Each strategy file adds only local symbols.

GitHub renders mathematics with `$inline$` and `$$display$$` delimiters. These notes are for research and implementation. They are not investment, legal, or tax advice.

## Options

All options in a given trade are on the same underlying unless noted. Same expiry $T$ unless the trade is a calendar or diagonal.

| Symbol | Definition |
|---|---|
| $S_0$ | underlying price at trade inception $t=0$ |
| $S_T$ | underlying price at expiry |
| $K, K_1, K_2, \ldots$ | strikes |
| $(x)_+$ | $\max(x,0)$ |
| $C$ | net credit received at $t=0$ |
| $D$ | net debit paid at $t=0$ |
| $H$ | $D$ on a net-debit trade, $-C$ on a net-credit trade |
| $f_T$ | terminal P&L including initial premium |
| $S^\ast$, $S^\ast_{\mathrm{up}}$, $S^\ast_{\mathrm{down}}$ | expiry break-evens |
| $P_{\max}$, $L_{\max}$ | maximum profit and maximum loss at expiry, ignoring financing and fees |
| ATM / ITM / OTM | at-, in-, out-of-the-money |

Greeks, when a file uses them:

$$
\Theta = \frac{\partial V}{\partial t}, \quad
\Delta = \frac{\partial V}{\partial S}, \quad
\Gamma = \frac{\partial^2 V}{\partial S^2}, \quad
\nu = \frac{\partial V}{\partial \sigma}
$$

## Equities and ETF cross-sections

| Symbol | Definition |
|---|---|
| $i = 1,\ldots,N$ | names in the universe |
| $P_i(t)$ | fully split- and dividend-adjusted price |
| $R_i(t)$ | simple return over the strategy’s native bar |
| $w_i$ | portfolio weight; $w_i>0$ long, $w_i<0$ short |
| $I$ | gross dollars, $I = I_L + I_S$ |
| dollar-neutral | $\sum_i w_i = 0$ and $\sum_i \lvert w_i\rvert = 1$ |
| long-only | $w_i \ge 0$ and $\sum_i w_i = 1$ |
| $T, S, H$ | formation, skip, and holding windows (typical equity momentum: $T=12$ months, $S=1$ month) |

## Fixed income

Zero price and continuously compounded yield:

$$
R(t,T) = -\frac{\ln P(t,T)}{T-t}
$$

Coupon bond:

$$
P_c(t,T) = P(t,T) + k\delta\sum_{i=I(t)}^n P(t,T_i)
$$

Macaulay / modified / dollar duration are the usual ones. Parallel-shift identities are local approximations. Slope and curvature trades are not immunized by a duration match alone.

## FX

| Symbol | Definition |
|---|---|
| $S(t)$ | spot FX, units of domestic per 1 unit of foreign |
| $F(t,T)$ | forward to tenor $T$ |
| $r_d, r_f$ | domestic and foreign risk-free rates over $T$ |
| $D(t,T)$ | forward discount $\ln S(t) - \ln F(t,T)$ |

Covered interest:

$$
F(t,T) = S(t)\,\frac{1+r_d}{1+r_f}
$$

## Volatility and indexes

Index variance from the weighted covariance of constituents:

$$
\sigma_I^2 = \sum_{i,j} w_i w_j \sigma_i \sigma_j \rho_{ij}
$$

VIX futures basis and daily roll:

$$
B_{\mathrm{VIX}} = P_{\mathrm{UX1}} - P_{\mathrm{VIX}}, \qquad D = \frac{B_{\mathrm{VIX}}}{T}
$$

Variance swap: $P(T) = N\bigl(v(T)-K\bigr)$ with

$$
v(T) = \frac{F}{T}\sum_t R(t)^2
$$

## Agent rules that apply to every file

1. Decision data at time $t$ uses only information with timestamp $< t$ (or $\le t$ if the file explicitly allows delay-0 at the open).
2. Output an intent blotter. Do not route live orders from these specs.
3. Do not implement venue exploits, spoofing, or unauthorized access.
4. FX triangular arb, index cash-and-carry, and same-index ETF arb are **research / delayed identity monitors**, not HFT playbooks.
5. Market-making is a **simulator / research spec** only.
