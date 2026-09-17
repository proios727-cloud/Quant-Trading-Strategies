"""Risk engine: fractional-Kelly sizing and a hard drawdown kill switch.

Reference spec: ``specs/mean_reversion.md`` sections 4.5 and 4.6.

Two jobs, in order:

1. **Size.** Fractional Kelly, ``f_t = clip(lambda * f*, +-l_max)``. Full Kelly
   is far too large at a 2-sigma deviation, and it is computed from an
   *estimated* drift, so it is unfractioned ruin. ``lambda`` and ``l_max`` are
   risk parameters, not knobs to tune until the backtest looks good.

2. **Stop.** A hard peak-to-trough drawdown latch (default 5%). On breach the
   book is flattened and no new position is taken.

Timing honesty (spec 4.6): ``DD_t`` is known at the close of ``t``, so the
breaching day's loss is *taken*. The earliest honest action is a flat position
for ``t+1``, which is what this engine does. A backtest that removes the
breaching day's loss is lying.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from strategy import kelly_leverage, target_weights as _target_weights

__all__ = [
    "RiskLimits",
    "DrawdownKillSwitch",
    "RiskReport",
    "RiskEngine",
]


# --------------------------------------------------------------------------
# Limits
# --------------------------------------------------------------------------


@dataclass
class RiskLimits:
    """Risk parameters. Defaults are the spec section 8 defaults."""

    kelly_fraction: float = 0.25      # lambda
    max_leverage: float = 1.0         # l_max, 1.0 means no borrowing
    max_drawdown: float = 0.05        # DD_max, peak-to-trough
    rearm: bool = False               # False = hard latch, never resume
    cooldown_days: int = 0            # bars flat before re-arming (if rearm)

    def __post_init__(self) -> None:
        if not 0.0 < self.kelly_fraction <= 1.0:
            raise ValueError("kelly_fraction must be in (0, 1]")
        if self.max_leverage <= 0.0:
            raise ValueError("max_leverage must be > 0")
        if not 0.0 < self.max_drawdown < 1.0:
            raise ValueError("max_drawdown must be in (0, 1)")
        if self.cooldown_days < 0:
            raise ValueError("cooldown_days must be >= 0")


# --------------------------------------------------------------------------
# Kill switch
# --------------------------------------------------------------------------


class DrawdownKillSwitch:
    """Hard peak-to-trough drawdown latch.

    Feed it equity, one bar at a time, in order. ``update`` returns whether the
    book must be flat. Once tripped the latch stays closed unless ``rearm`` is
    set and the cooldown has elapsed.
    """

    def __init__(
        self,
        max_drawdown: float = 0.05,
        rearm: bool = False,
        cooldown_days: int = 0,
    ) -> None:
        if not 0.0 < max_drawdown < 1.0:
            raise ValueError("max_drawdown must be in (0, 1)")
        self.max_drawdown = float(max_drawdown)
        self.rearm = bool(rearm)
        self.cooldown_days = int(cooldown_days)

        self.peak: float = -np.inf
        self.drawdown: float = 0.0
        self.halted: bool = False
        self.breaches: int = 0
        self.breach_dates: list = []
        self._cooldown_left: int = 0

    # -- internals ---------------------------------------------------------

    def _trip(self, date) -> None:
        self.halted = True
        self.breaches += 1
        self.breach_dates.append(date)
        self._cooldown_left = self.cooldown_days

    # -- public ------------------------------------------------------------

    def update(self, equity: float, date=None) -> bool:
        """Mark equity to market and return ``True`` if the book must be flat."""
        e = float(equity)
        if not np.isfinite(e):
            return self.halted

        if e > self.peak:
            self.peak = e

        # Peak can be 0 or negative only for a degenerate equity path; guard it.
        if self.peak > 0.0:
            self.drawdown = (self.peak - e) / self.peak
        else:
            self.drawdown = 0.0

        if not self.halted:
            if self.drawdown >= self.max_drawdown:
                self._trip(date)
        elif self.rearm:
            if self._cooldown_left > 0:
                self._cooldown_left -= 1
            else:
                # Resume from the current level; do not inherit the old peak,
                # or the latch would trip again on the next tick.
                self.halted = False
                self.peak = e
                self.drawdown = 0.0

        return self.halted


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


@dataclass
class RiskReport:
    """Executed book, equity path, and kill-switch metadata."""

    frame: pd.DataFrame
    limits: RiskLimits
    breaches: int = 0
    first_breach: Optional[pd.Timestamp] = None
    halted_at_end: bool = False
    max_drawdown_realized: float = 0.0
    breach_dates: list = field(default_factory=list)

    @property
    def equity(self) -> pd.Series:
        return self.frame["equity"]

    @property
    def executed_weights(self) -> pd.Series:
        return self.frame["executed_weight"]

    @property
    def tripped(self) -> bool:
        return self.breaches > 0

    def summary(self) -> dict:
        return {
            "breaches": self.breaches,
            "first_breach": self.first_breach,
            "halted_at_end": self.halted_at_end,
            "max_drawdown_realized": self.max_drawdown_realized,
            "final_equity": float(self.frame["equity"].iloc[-1])
            if len(self.frame)
            else np.nan,
        }


# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------


class RiskEngine:
    """Fractional-Kelly sizing plus the drawdown kill switch."""

    def __init__(self, limits: Optional[RiskLimits] = None) -> None:
        self.limits = limits or RiskLimits()
        self.switch: Optional[DrawdownKillSwitch] = None

    # -- sizing ------------------------------------------------------------

    def kelly(self, z, sigma_eq) -> pd.Series:
        """Signed fractional-Kelly leverage, capped at ``max_leverage``."""
        return kelly_leverage(
            z,
            sigma_eq,
            kelly_fraction=self.limits.kelly_fraction,
            max_leverage=self.limits.max_leverage,
        )

    def target_weights(self, signal, z, sigma_eq) -> pd.Series:
        """Pre-kill-switch target weights ``D_t = q_t * |f_t|``."""
        return _target_weights(
            signal,
            z,
            sigma_eq,
            kelly_fraction=self.limits.kelly_fraction,
            max_leverage=self.limits.max_leverage,
        )

    # -- execution ---------------------------------------------------------

    def apply(
        self,
        weights,
        returns,
        init_equity: float = 1.0,
    ) -> RiskReport:
        """Walk the book forward, applying the kill switch to the equity path.

        ``weights[t]`` is the target decided with information through ``t`` and
        earns ``returns[t]``. A breach observed at ``t`` flattens from ``t+1``.
        """
        w = pd.Series(weights, dtype=float)
        r = pd.Series(returns, dtype=float).reindex(w.index).fillna(0.0)

        switch = DrawdownKillSwitch(
            max_drawdown=self.limits.max_drawdown,
            rearm=self.limits.rearm,
            cooldown_days=self.limits.cooldown_days,
        )
        self.switch = switch

        n = len(w)
        w_arr = w.to_numpy(dtype=float)
        r_arr = r.to_numpy(dtype=float)

        executed = np.zeros(n, dtype=float)
        equity = np.zeros(n, dtype=float)
        drawdown = np.zeros(n, dtype=float)
        halted = np.zeros(n, dtype=bool)

        e = float(init_equity)
        if not np.isfinite(e) or e <= 0.0:
            raise ValueError("init_equity must be finite and > 0")

        for t in range(n):
            # Decide the position for bar t. If the latch is already closed we
            # are flat -- this is the flattening that follows a breach.
            if switch.halted:
                w_t = 0.0
            else:
                w_t = w_arr[t]
                if not np.isfinite(w_t):
                    w_t = 0.0

            executed[t] = w_t
            e *= 1.0 + w_t * r_arr[t]
            if not np.isfinite(e):
                e = 0.0
            e = max(e, 0.0)
            equity[t] = e

            switch.update(e, date=w.index[t])
            drawdown[t] = switch.drawdown
            halted[t] = switch.halted

        frame = pd.DataFrame(
            {
                "target_weight": w_arr,
                "executed_weight": executed,
                "returns": r_arr,
                "equity": equity,
                "drawdown": drawdown,
                "halted": halted,
            },
            index=w.index,
        )

        return RiskReport(
            frame=frame,
            limits=self.limits,
            breaches=switch.breaches,
            first_breach=switch.breach_dates[0] if switch.breach_dates else None,
            halted_at_end=switch.halted,
            max_drawdown_realized=float(np.nanmax(drawdown)) if n else 0.0,
            breach_dates=list(switch.breach_dates),
        )

    def run(
        self,
        signal,
        z,
        sigma_eq,
        returns,
        init_equity: float = 1.0,
    ) -> RiskReport:
        """Size, then apply the kill switch."""
        weights = self.target_weights(signal, z, sigma_eq)
        return self.apply(weights, returns, init_equity=init_equity)
