"""Balanced crossed Gauge R&R using the random-effects ANOVA method."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GageRRResult:
    parts: int
    operators: int
    trials: int
    repeatability_variance: float
    operator_variance: float
    interaction_variance: float
    reproducibility_variance: float
    gage_rr_variance: float
    part_to_part_variance: float
    total_variance: float
    percent_contribution_grr: float
    percent_study_variation_grr: float
    percent_study_variation_repeatability: float
    percent_study_variation_reproducibility: float
    ndc: int
    interpretation: str

    def to_dict(self) -> dict:
        return asdict(self)


def crossed_gage_rr(
    frame: pd.DataFrame, *, part_col: str = "part_id", operator_col: str = "operator",
    value_col: str = "measurement_mm",
) -> GageRRResult:
    """Analyze a complete, balanced, crossed part/operator/repeat design."""
    required = {part_col, operator_col, value_col}
    if not required <= set(frame.columns):
        raise ValueError(f"Gauge R&R data require columns: {sorted(required)}")
    data = frame[list(required)].copy()
    data[value_col] = pd.to_numeric(data[value_col], errors="raise")
    if data[value_col].isna().any() or not np.isfinite(data[value_col]).all():
        raise ValueError("Measurements must be finite and complete")
    counts = data.groupby([part_col, operator_col]).size()
    if counts.empty or counts.nunique() != 1 or counts.iloc[0] < 2:
        raise ValueError("Design must be balanced with at least two repeats per part/operator cell")
    p = data[part_col].nunique(); o = data[operator_col].nunique(); r = int(counts.iloc[0])
    if len(data) != p * o * r or p < 2 or o < 2:
        raise ValueError("Every operator must measure every part for the same number of trials")

    grand = data[value_col].mean()
    part_means = data.groupby(part_col)[value_col].mean()
    op_means = data.groupby(operator_col)[value_col].mean()
    cell_means = data.groupby([part_col, operator_col])[value_col].mean()
    ss_part = o * r * ((part_means - grand) ** 2).sum()
    ss_op = p * r * ((op_means - grand) ** 2).sum()
    ss_interaction = 0.0
    for (part, operator), cell_mean in cell_means.items():
        ss_interaction += r * (cell_mean - part_means[part] - op_means[operator] + grand) ** 2
    joined = data.join(cell_means.rename("cell_mean"), on=[part_col, operator_col])
    ss_error = ((joined[value_col] - joined.cell_mean) ** 2).sum()
    ms_part = ss_part / (p - 1)
    ms_op = ss_op / (o - 1)
    ms_interaction = ss_interaction / ((p - 1) * (o - 1))
    ms_error = ss_error / (p * o * (r - 1))

    var_repeat = max(float(ms_error), 0.0)
    var_interaction = max(float((ms_interaction - ms_error) / r), 0.0)
    var_operator = max(float((ms_op - ms_interaction) / (p * r)), 0.0)
    var_part = max(float((ms_part - ms_interaction) / (o * r)), 0.0)
    var_repro = var_operator + var_interaction
    var_grr = var_repeat + var_repro
    var_total = var_grr + var_part
    sd_total = np.sqrt(var_total)
    pct_sv_grr = 100 * np.sqrt(var_grr) / sd_total if sd_total else 0.0
    pct_contribution = 100 * var_grr / var_total if var_total else 0.0
    pct_repeat = 100 * np.sqrt(var_repeat) / sd_total if sd_total else 0.0
    pct_repro = 100 * np.sqrt(var_repro) / sd_total if sd_total else 0.0
    ndc = int(np.floor(1.41 * np.sqrt(var_part) / np.sqrt(var_grr))) if var_grr else 99
    if pct_sv_grr < 10:
        interpretation = "Generally acceptable"
    elif pct_sv_grr <= 30:
        interpretation = "May be acceptable depending on application"
    else:
        interpretation = "Generally unacceptable; improve the measurement system"
    return GageRRResult(
        parts=p, operators=o, trials=r, repeatability_variance=var_repeat,
        operator_variance=var_operator, interaction_variance=var_interaction,
        reproducibility_variance=var_repro, gage_rr_variance=var_grr,
        part_to_part_variance=var_part, total_variance=var_total,
        percent_contribution_grr=pct_contribution,
        percent_study_variation_grr=pct_sv_grr,
        percent_study_variation_repeatability=pct_repeat,
        percent_study_variation_reproducibility=pct_repro,
        ndc=ndc, interpretation=interpretation,
    )
