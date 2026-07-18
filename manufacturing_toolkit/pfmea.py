"""PFMEA data validation, RPN calculation, and action tracking."""

from __future__ import annotations

import pandas as pd

REQUIRED = {
    "process_step", "failure_mode", "effect", "cause", "current_control",
    "severity", "occurrence", "detection",
}


def _priority(rpn: int, severity: int) -> str:
    """Transparent portfolio triage—not the AIAG-VDA proprietary AP table."""
    if severity >= 9 or rpn >= 200:
        return "High"
    if severity >= 7 or rpn >= 100:
        return "Medium"
    return "Low"


def analyze_pfmea(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing PFMEA columns: {sorted(missing)}")
    result = frame.copy()
    for column in ("severity", "occurrence", "detection"):
        result[column] = pd.to_numeric(result[column], errors="raise").astype(int)
        if not result[column].between(1, 10).all():
            raise ValueError(f"{column} ratings must be integers from 1 to 10")
    result["rpn"] = result.severity * result.occurrence * result.detection
    result["portfolio_priority"] = [
        _priority(rpn, severity) for rpn, severity in zip(result.rpn, result.severity)
    ]
    if {"revised_severity", "revised_occurrence", "revised_detection"} <= set(result.columns):
        for column in ("revised_severity", "revised_occurrence", "revised_detection"):
            result[column] = pd.to_numeric(result[column], errors="raise").astype(int)
            if not result[column].between(1, 10).all():
                raise ValueError(f"{column} ratings must be integers from 1 to 10")
        result["revised_rpn"] = (
            result.revised_severity * result.revised_occurrence * result.revised_detection
        )
        result["risk_reduction_percent"] = (1 - result.revised_rpn / result.rpn) * 100
    return result.sort_values(["rpn", "severity"], ascending=False).reset_index(drop=True)
