"""Fun little example using the example of a Bond class."""

import math
from datetime import date
from typing import Any, Self, TypeVar

import numpy as np
from numpy.typing import NDArray

from nodeify import Graph, node

DateType = TypeVar(
    "DateType",
    date,
    list[date],
    np.datetime64,
    list[np.datetime64],
    NDArray[np.datetime64],
)


# TODO: make a graph?
class YieldCurve:
    """An exmaple yield curve. Zero curve, continuous basis, no need to parameterize."""

    def __init__(
        self: Self, curve_dt: date, x: NDArray[np.float64], y: NDArray[np.float64]
    ) -> None:
        self.curve_dt = curve_dt
        self.x = x
        self.y = y

    def rate(self: Self, dt: DateType) -> NDArray[np.float64]:
        dt_ = np.asarray(dt, dtype="datetime64[D]")
        x = np.asarray(dt_ - np.datetime64(self.curve_dt, "D"), dtype=np.float64)
        return np.interp(x=x, xp=self.x, fp=self.y)

    def pv(self: Self, dt: DateType, oas: float) -> NDArray[np.float64]:
        """Compute the PV of 1 unit of the numeraire represented by this curve."""
        dt_ = np.asarray(dt, dtype="datetime64[D]")
        rate = self.rate(dt_) + oas
        t = np.asarray(dt_ - np.datetime64(self.curve_dt, "D"), dtype=np.float64)
        return np.exp(-rate * t)


class Bond(Graph):
    """Lazily re-evaluating bond model. Outrageously simplified example."""

    def __init__(
        self: Self,
        price: float,
        pricing_curve: YieldCurve,
        oas: float,
        **_: Any,
    ) -> None:
        self.price = price
        self.pricing_curve = pricing_curve
        self.oas = oas

    @property
    def schedule(self: Self) -> NDArray[np.datetime64]:
        """Hypothetical semiannual bond with dated dt 2/15/24"""
        dt = np.arange("2024-02", "2034-03", step=np.timedelta64(6, "M"), dtype="M8[M]")
        return dt[1:].astype("M8[D]") + np.timedelta64(14, "D")  # type: ignore

    @property
    def cashflows(self: Self) -> NDArray[np.float64]:
        """Assuming 4% semi bond with ACT/ACT ICMA daycount, e.g. US TSY-like"""
        cfs = np.full(shape=self.schedule.shape, fill_value=2e-2, dtype=np.float64)
        cfs[-1] += 1.0
        return cfs

    @node
    def price(self: Self) -> float:
        oas = self.oas
        if oas is None or math.isnan(oas):
            oas = 0.0

        dfs = self.pricing_curve.pv(self.schedule, oas)
        cfs = self.cashflows

        return np.sum(cfs * dfs).item()

    @node
    def oas(self: Self) -> float:
        return 0.0

    @node
    def pricing_curve(self: Self) -> YieldCurve: ...  # type: ignore[empty-body]
