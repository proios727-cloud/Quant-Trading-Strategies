---
rank: 84
slug: swap-spread-arbitrage
title: "Swap-Spread Arbitrage"
asset_class: "fixed income"
style: "swap vs Treasury / LIBOR-repo spread bet"
horizon: "Hold to a spread target or to a funding event"
instruments: "interest-rate swap and a same-maturity Treasury; repo financing"
---

# 084. Swap-Spread Arbitrage

| Field | Value |
|---|---|
| Popularity rank (this kit) | 84 of 101 |
| Why it sits here | Long (short) swap vs short (long) matched-maturity Treasury. A LIBOR–repo / swap-spread view, not a free arb. |
| Aliases | swap spread, LIBOR-repo, SOFR-Treasury spread |
| Asset class | fixed income |
| Style | swap vs Treasury / LIBOR-repo spread bet |
| Typical horizon | Hold to a spread target or to a funding event |
| Instruments | interest-rate swap and a same-maturity Treasury; repo financing |

Shared symbols live in [`_shared-notation.md`](_shared-notation.md).

## 1. Overview

A duration-matched long receive-fixed swap versus a short Treasury (financed in repo) earns the swap spread minus the LIBOR (or replacement-rate) versus repo gap. Reverse the book to short the spread. This is a view on swap spreads and on funding, not a locked arbitrage.

Monitor SOFR (or the actual floating index) versus the old LIBOR notation. You are not trading CDS basis (file 059) and you are not running a three-bond fly (file 083). You are matching a swap to a Treasury and warehousing $C_1$ versus a moving $C_2(t)$.

Typical users are rates RV desks with swap lines and repo. Horizon is until a spread target or a funding event, not a Sharpe-maximising hold that ignores VM. Special repo can dominate $C_2$. Haircuts on the Treasury short are first-order cash: $I$ of face is not $I$ of capital. Delay-1: marks dated $\le t$. Using LIBOR after the swap has moved to SOFR is a failed spec. A “cheap” $C_1$ on a specials day is usually $C_2$, not a free lunch.

## 2. First principles

Take a matched-maturity par swap with fixed rate $r_{\mathrm{swap}}$ and a Treasury yielding $Y_{\mathrm{Treasury}}$. The structural spread collected (or paid) on a dollar-neutral, DV01-matched package is the difference of two carry legs. The first is the swap-versus-Treasury coupon gap, constant on the trade date:

$$
C_1 = r_{\mathrm{swap}} - Y_{\mathrm{Treasury}}
$$

$C_1$ is the swap spread in coupon units, frozen at entry until you re-strike. It is not a locked profit: the floating and repo legs still move. Mixing a par swap rate with a CTD yield without conversion factors will invent $C_1$.

The second is the floating index minus repo, which moves every day:

$$
C_2(t)=L(t)-r(t)
$$

$L(t)$ is LIBOR or its replacement (SOFR plus spread, or the swap’s actual floating index). $r(t)$ is the repo rate on the Treasury. Specials make $r(t)$ jump independently of $L(t)$. Per dollar, signed carry is

$$
C(t)=\pm\bigl[C_1 - C_2(t)\bigr]
$$

Plus = long-swap book: receive fixed on the swap, pay $L$, short the Treasury, reverse-repo the short (or long-swap vs short cash bond financed at $r$). Profitable if $L$ falls relative to repo (long swap) or rises (short swap). It is a floating-index-versus-repo bet, plus a swap-spread level bet through $C_1$.

That is the whole package. Everything below is DV01 matching, haircuts, and how not to look ahead. If you skip DV01 matching, a parallel yield move will swamp $C(t)$. If you skip specials, $C_2$ is fiction. If you skip the floating-index map, a SOFR swap marked on LIBOR is a different product with a made-up residual.

## 3. Notation

| Symbol | Definition |
|---|---|
| $r_{\mathrm{swap}}$ | swap fixed rate |
| $Y_{\mathrm{Treasury}}$ | matched-maturity Treasury yield |
| $L(t)$ | floating index (LIBOR or replacement) |
| $r(t)$ | repo on the Treasury |
| $C_1$ | $r_{\mathrm{swap}}-Y_{\mathrm{Treasury}}$ |
| $C_2(t)$ | $L(t)-r(t)$ |
| $C(t)$ | signed carry per dollar |
| $\mathrm{DD}$ | dollar duration of each leg |
| $I$ | gross dollars on the Treasury leg |
| $h$ | haircut |

## 4. Mathematics

### 4.1 Carry identity

Per dollar:

$$
C(t)=\pm\bigl[C_1 - C_2(t)\bigr]
$$

The sign is the side of the book, not a hidden option. Entry when $\lvert C_1-C_2\rvert$ exceeds costs and haircut drag. A mid-to-mid $C$ that ignores specials is not a gate.

$$
C_1 = r_{\mathrm{swap}} - Y_{\mathrm{Treasury}}
$$

Frozen at trade date until you unwind or recoupon. Permuting next month’s swap rate must not change today’s $C_1$.

$$
C_2(t)=L(t)-r(t)
$$

This is the daily funding residual. $L(t)$ must be the swap’s actual floating index. Stale LIBOR on a SOFR swap is a failed spec.

Plus = long-swap book. Entry when $\lvert C_1-C_2\rvert$ exceeds costs and haircut drag.

### 4.2 DV01 match

Match maturity and DV01, not just par. Set swap notional so $\mathrm{DD}_{\mathrm{swap}}=\mathrm{DD}_{\mathrm{Treasury}}$ at entry, and re-hedge when residual DV01 exceeds a tolerance. Haircuts on the Treasury short/long change the cash outlay but not the first-order rates identity if variation margin is posted. Par-notional matching of a 10y swap to $I$ of a 10y Treasury leaves a duration residual whenever DV01s differ.

### 4.3 Holding-period P&L

Swap MtM plus Treasury price change plus coupons minus repo (including specials) minus costs:

$$
\mathrm{P\&L} = \mathrm{swap}_{\mathrm{MtM}} + \Delta P_{\mathrm{Treasury}} + \mathrm{coupons} - \mathrm{repo} - \mathrm{costs}
$$

Duration P&L $\approx -\mathrm{DD}\,\Delta y$ on each leg should nearly cancel if DV01 stayed matched. Report P&L, $C(t)$, residual DV01, and funding events. A Sharpe that drops funding-event weeks is not an acceptance.

## 5. Step-by-step algorithm

1. **Tenor.** Default 10y swap versus 10y Treasury (or the CTD if using futures). This step exists so a 2y swap versus a 10y bond is not called a swap-spread package.
2. **Marks.** $r_{\mathrm{swap}}$, $Y_{\mathrm{Treasury}}$, $L(t)$, $r(t)$ dated $\le t$. Specials known after $t$ do not belong in the $t$ gate.
3. **Carry.** Compute $C_1$, $C_2$, $C$. Gate on $C$ versus costs. Flat is valid.
4. **Match.** DV01-match notionals. Apply haircut $h$ to cash usage. Ignoring $h$ understates cash and overstates how large $I$ can be.
5. **Index.** Replace $L(t)$ with the swap floating index actually used (SOFR, etc.). Do not keep a LIBOR series out of habit.
6. **Blotter.** Swap + Treasury (or futures) intents. Do not route live orders.
7. **Re-hedge.** When DV01 drifts or the CTD switches. A conversion-factor jump is a discrete $D$ change.
8. **Exit.** Spread target, stop on a funding event, or max hold. Averaging a widening spread into a funding squeeze is how 2008 books died.

## 6. Execution protocol

- Default fill: next close. Delay-0 is research-only. Filling on the same print that just moved $r_{\mathrm{swap}}$ uses a $C_1$ that was not known at the decision stamp.
- Monitor SOFR/LIBOR transition: replace $L(t)$ with the swap floating index actually used. A hardcoded LIBOR series after 2023 is almost always wrong.
- Special repo can dominate $C_2$. A “cheap” swap spread on a specials day is not a free lunch. Pull specials from the same timestamp convention as $r(t)$, not from a weekly GC average.
- Haircuts on the Treasury short/long are first-order cash. If $h$ is missing, the engine will size $I$ as if unlevered cash were infinite.

## 7. Data contract

Required, point-in-time:

- Swap rate, floating-index prints, and swap DV01
- Treasury clean/dirty price, yield, duration
- Repo (general and specials)
- Haircuts and CCP/VM terms
- If futures: conversion factor and CTD

Not used by this spec: CDS, equity book value, earnings, SUE, COT.

No look-ahead on $L(t)$ or on unannounced specials. A specials print that hits after the close does not change the $t$ $C_2$ used for the gate, though it will change later P&L. CCP variation-margin terms belong in cash usage: a duration-matched package can still fail a cash limit. If the swap and the Treasury do not share a maturity bucket, stop; that is a curve trade plus a swap spread, not this file.

## 8. Parameters and defaults

| Parameter | Default | Notes |
|---|---|---|
| tenor | 10y | |
| entry | $C_1-C_2$ vs costs | |
| $L(t)$ | swap floating index | not stale LIBOR if the swap is SOFR |
| $\beta$ on yields | 1 | unless a documented residual beta |
| delay | 1 bar | delay-0 is research-only |

## 9. Agent implementation contract

Build a Python module `strategies.swap_spread_arbitrage` with:

1. `C1(r_swap, y_treasury) -> float` — $r_{\mathrm{swap}}-Y_{\mathrm{Treasury}}$.
2. `C2(L, repo) -> float` — $L(t)-r(t)$.
3. `carry(C1, C2, side) -> float` — $\pm(C_1-C_2)$.
4. `match_dv01(DD_swap, DD_trsy, I) -> dict` — notionals.
5. `blotter(side, notionals, lot) -> list[OrderIntent]` — never live routing.
6. `pnl(swap_mtm, dP, coupons, repo, costs) -> float` — matches 4.3.

Refuse venue exploits, spoofing, or unauthorized access.

## 10. Risks and failure modes

- **Swap-spread dislocation.** 2008-style basis blowouts. $C_1$ can move against you while $C_2$ also jumps.
- **Repo specials.** $C_2$ can jump independently of $C_1$. Treating GC as $r(t)$ on a specials day invents carry.
- **Counterparty / CCP.** Swap MtM and VM. A hedge that is duration-matched can still cash-crunch.
- **Index reform.** Using LIBOR after the swap has moved to SOFR is a failed spec.
- **CTD.** Futures implementations inherit delivery optionality.
- **Par matching.** Equal par notionals without DV01 match leave a rates residual labeled as “swap spread.”

## 11. Acceptance tests

- $C_1$, $C_2$, and $C=\pm(C_1-C_2)$ to `1e-8` on a toy quote.
- DV01-matched parallel $\Delta y$ → first-order net duration P&L $\approx 0$.
- Permuting $L$ and repo after $t$ must not change the $t$ entry $C_1$ (only $C_2$ at later bars).
- Adding linear costs $\tau$ or a worse repo weakly decreases P&L.
- A SOFR swap must not accept a LIBOR $L(t)$ without a documented fallback spread.
- Haircut $h>0$ must increase cash usage versus $h=0$ on the same $I$ of face; a test that ignores $h$ is not this spec.

## 12. References

- Use this file as the source of truth for formulas, signals, data, and the agent contract.

---

*Research spec for quantitative work. Not investment advice.*
