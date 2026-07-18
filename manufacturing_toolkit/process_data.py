"""Pareto and individuals/moving-range process-data analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def pareto_summary(frame: pd.DataFrame, category: str, value: str | None = None) -> pd.DataFrame:
    if category not in frame:
        raise ValueError(f"Missing category column: {category}")
    if value is None:
        summary = frame.groupby(category).size().rename("count").reset_index()
    else:
        if value not in frame:
            raise ValueError(f"Missing value column: {value}")
        summary = frame.groupby(category)[value].sum().rename("count").reset_index()
    summary = summary.sort_values("count", ascending=False).reset_index(drop=True)
    total = summary["count"].sum()
    summary["percent"] = summary["count"] / total * 100 if total else 0.0
    summary["cumulative_percent"] = summary.percent.cumsum()
    return summary


def imr_chart_data(values) -> dict[str, np.ndarray | float]:
    """Return I-MR limits based on consecutive moving ranges of length two."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size < 3 or not np.isfinite(x).all():
        raise ValueError("I-MR analysis requires at least three finite ordered values")
    mr = np.abs(np.diff(x)); mr_bar = float(mr.mean()); center = float(x.mean())
    sigma = mr_bar / 1.128
    return {
        "values": x, "moving_ranges": mr, "center": center,
        "i_ucl": center + 3 * sigma, "i_lcl": center - 3 * sigma,
        "mr_center": mr_bar, "mr_ucl": 3.267 * mr_bar, "mr_lcl": 0.0,
        "estimated_sigma": sigma,
    }
