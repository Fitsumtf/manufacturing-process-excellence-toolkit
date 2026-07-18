"""Validated Cp/Cpk calculations for dimensional manufacturing data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass(frozen=True)
class CapabilityResult:
    n: int
    mean: float
    target: float
    sample_stdev: float
    population_stdev: float
    lsl: float
    usl: float
    cp: float
    cpu: float
    cpl: float
    cpk: float
    six_sigma_spread: float
    spec_width: float
    observed_rejects: int
    observed_ppm: float
    expected_ppm_normal: float
    status: str

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def load_measurements(path: str | Path, column: str = "measurement_mm") -> np.ndarray:
    """Load a finite numeric measurement column from CSV."""
    frame = pd.read_csv(path)
    if column not in frame.columns:
        raise ValueError(f"CSV must contain a '{column}' column")
    series = pd.to_numeric(frame[column], errors="coerce")
    if series.isna().any():
        bad_rows = (series[series.isna()].index + 2).tolist()
        raise ValueError(f"Non-numeric or missing measurements at CSV rows: {bad_rows}")
    values = series.to_numpy(dtype=float)
    if values.size < 2:
        raise ValueError("At least two measurements are required")
    if not np.isfinite(values).all():
        raise ValueError("Measurements must be finite")
    return values


def capability_status(cpk: float) -> str:
    if cpk < 1.00:
        return "Not capable"
    if cpk < 1.33:
        return "Marginal"
    if cpk < 1.67:
        return "Generally capable"
    if cpk < 2.00:
        return "Strong capability"
    return "Very high capability"


def analyze_capability(
    values: np.ndarray | list[float], *, lsl: float, usl: float, target: float
) -> CapabilityResult:
    """Calculate two-sided short-term capability using sample standard deviation."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size < 2 or not np.isfinite(x).all():
        raise ValueError("values must be a finite one-dimensional array with n >= 2")
    if not lsl < target < usl:
        raise ValueError("Expected LSL < target < USL")

    mean = float(np.mean(x))
    sample_stdev = float(np.std(x, ddof=1))
    population_stdev = float(np.std(x, ddof=0))
    if sample_stdev <= 0:
        raise ValueError("Capability is undefined when sample standard deviation is zero")

    cp = (usl - lsl) / (6.0 * sample_stdev)
    cpu = (usl - mean) / (3.0 * sample_stdev)
    cpl = (mean - lsl) / (3.0 * sample_stdev)
    cpk = min(cpu, cpl)
    observed_rejects = int(np.count_nonzero((x < lsl) | (x > usl)))
    expected_fraction = norm.cdf((lsl - mean) / sample_stdev) + norm.sf(
        (usl - mean) / sample_stdev
    )

    return CapabilityResult(
        n=int(x.size), mean=mean, target=float(target), sample_stdev=sample_stdev,
        population_stdev=population_stdev, lsl=float(lsl), usl=float(usl),
        cp=float(cp), cpu=float(cpu), cpl=float(cpl), cpk=float(cpk),
        six_sigma_spread=6.0 * sample_stdev, spec_width=usl - lsl,
        observed_rejects=observed_rejects,
        observed_ppm=observed_rejects / x.size * 1_000_000.0,
        expected_ppm_normal=float(expected_fraction * 1_000_000.0),
        status=capability_status(cpk),
    )
