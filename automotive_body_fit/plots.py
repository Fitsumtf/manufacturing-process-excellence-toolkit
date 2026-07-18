"""Engineering plots for capability reporting."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from .analysis import CapabilityResult


def _style() -> None:
    plt.rcParams.update({"figure.dpi": 150, "axes.grid": True, "grid.alpha": 0.22})


def capability_histogram(values: np.ndarray, result: CapabilityResult, path: Path) -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.hist(values, bins="auto", density=True, color="#337AA5", alpha=0.78, edgecolor="white")
    grid = np.linspace(min(values.min(), result.lsl) - 0.08, max(values.max(), result.usl) + 0.08, 500)
    ax.plot(grid, norm.pdf(grid, result.mean, result.sample_stdev), color="#17324D", lw=2, label="Normal fit")
    ax.axvline(result.lsl, color="#B23A48", lw=2, label=f"LSL {result.lsl:.3f}")
    ax.axvline(result.usl, color="#B23A48", lw=2, label=f"USL {result.usl:.3f}")
    ax.axvline(result.target, color="#2A9D62", lw=2, ls="--", label=f"Target {result.target:.3f}")
    ax.set(title="Body-Fit Gap Capability Distribution", xlabel="Gap (mm)", ylabel="Density")
    ax.legend(ncol=4, fontsize=8, loc="upper center")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def run_chart(values: np.ndarray, result: CapabilityResult, path: Path) -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    samples = np.arange(1, values.size + 1)
    ax.plot(samples, values, color="#337AA5", marker="o", ms=3, lw=1)
    failed = (values < result.lsl) | (values > result.usl)
    ax.scatter(samples[failed], values[failed], color="#B23A48", s=45, zorder=4, label="Out of specification")
    ax.axhline(result.lsl, color="#B23A48", lw=1.6, label="Specification limits")
    ax.axhline(result.usl, color="#B23A48", lw=1.6)
    ax.axhline(result.target, color="#2A9D62", lw=1.5, ls="--", label="Target")
    ax.set(title="Time-Ordered Measurement Run Chart", xlabel="Sample sequence", ylabel="Gap (mm)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
